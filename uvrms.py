#! /usr/bin/env python
import numpy as np
import os
import argparse
from uvdata.uv import UVData
import math
from uvcache import UVCache
import sys
from tqdm import trange


# options parser for min and max frequency and time
parser = argparse.ArgumentParser()
parser.add_argument('mir', help='Path of input Miriad file')
parser.add_argument('out', help='Path of output Numpy binary file')
parser.add_argument('-d', action='store_true',
                    help="Enable directory mode.  Useful when data is distributed in a series of input files.")
parser.add_argument('-t', '--times', type=str, default="1",
                    help="Number of integrations to take RMSE over.  Defaults to 1.  Default unit is integrations - use s to specify seconds, e.g. 120s")
parser.add_argument('-f', '--freq', type=str, default="1",
                    help="Number of frequencies/channels to take RMSE over.  Defaults to 1.  Default unit is channels - use MHz to specify frequency range")
parser.add_argument('-s', '--suff', type=str, default="",
                    help="Suffix of files to process.  Helpful if directory contains non-differenced files")
parser.add_argument('--tsplit', action='store_true',
                    help="Hacky way of dealing with time-subtracted files")
args = parser.parse_args()
# read in the filenames from the directory
files = []
filenames = []
if args.d:
    contents = os.listdir(args.mir)
    for i in range(0, len(contents)):
        if contents[i].endswith(args.suff):
            files.append(args.mir + contents[i])
            filenames.append(os.path.basename(contents[i]))

else:
    files = [args.mir]
files.sort()
# parse first and last time
# here assuming files are named with julian date and time or similar
# scheme such that alphabetical order is time order.  may need to tweak at
# a later date. basically we just want to avoid having to open every
# single file
uva, uvz = UVData(), UVData()
uva.read_miriad(files[0])
uvz.read_miriad(files[-1])
first_time = uva.time_array[0]
last_time = uvz.time_array[-1]
integration_time = uva.integration_time
if args.tsplit:
    integration_time *= 2
channel_width = uva.channel_width
# process args
try:
    args.times = int(float(args.times))
    print "Calculating over {0} integrations.".format(args.times)
except:
    if args.times[-1:] == 's':
        args.times = int(
            math.ceil(float(args.times[:-1]) / integration_time))
        print "Calculating over {0} integrations.".format(args.times)
    elif args.times[-3:] == 'min':
        args.times = int(math.ceil(
            60 * float(args.times[:-3]) / integration_time))
        print "Calculating over {0} integrations.".format(args.times)
    elif args.times[-1:] == 'h':
        args.times = int(math.ceil(
            3600 * float(args.times[:-1]) / integration_time))
        print "Calculating over {0} integrations.".format(args.times)
    else:
        print "Could not determine RMS dimension for time"
        sys.exit()
try:
    args.freq = int(float(args.freq))
    print "Calculating over {0} frequency channels.".format(args.freq)
except:
    if args.freq[-3:] == 'MHz':
        args.freq = int(
            math.ceil(int(1e6 * float(args.freq[:-3])) / channel_width))
        print "Calculating over {0} frequency channels.".format(args.freq)
    else:
        print "Could not determine RMS dimension for channels"
        sys.exit()
Nfreqs = uva.Nfreqs
Nbls = uva.Nbls
Nspws = uva.Nspws
Npols = uva.Npols
Nblts = uva.Nblts
baseline_array = uva.baseline_array[0:Nbls]
spw_array = uva.spw_array
polarization_array = uva.polarization_array
# check input validity
Ntimes = uva.Ntimes * (len(files) - 1) + uvz.Ntimes
if Ntimes < args.times:
    print "Warning: fewer time samples than requested time RMSE window.  Result will be single value."
    args.times = Ntimes
if Nfreqs < args.freq:
    print "Warning: fewer frequency samples than requested frequency RMSE window.  Result will be single value."
    args.freq = Nfreqs
# calculate samples to average in each dimension
tsamps = int(Ntimes / args.times)
fsamps = int(Nfreqs / args.freq)
# instantiate arrays for storing RMSE and number of samples per RMS value
rms_array = np.ndarray((Nbls, tsamps, Nspws, fsamps, Npols))
nsample_array = np.ndarray((Nbls, tsamps, Nspws, fsamps, Npols))
time_array = np.ndarray((tsamps,))
lst_array = np.ndarray((tsamps,))
freq_array = np.ndarray((fsamps,))
print "Output dimensions:{0}".format(rms_array.shape)
# create a buffer of uvdata objects big enough to accomodate integration window
size = int(math.ceil(float(args.times) / float(uva.Ntimes))) + 1
uvs = UVCache(files, size)
# fill out a header with useful info
header = {'rms_shape': [args.times, args.freq],
          'filenames': filenames, 'args': args}
for uvp in ['Nbls', 'Nfreqs', 'Npols', 'Nspws', 'Ntimes', 'Nblts', 'integration_time', 'channel_width', 'object_name', 'telescope_name', 'instrument', 'telescope_location', 'history']:
    header[uvp] = getattr(uva, uvp)
del uva
del uvz
first_time = True
for t in trange(tsamps):
    for spw in range(Nspws):
        for f in trange(fsamps):
            for pol in range(Npols):
                data = uvs.get_sub_array(
                    [Nbls * t * args.times, spw, f * args.freq, pol], [Nbls * args.times, 1, args.freq, 1])
                # work around to handle the raveling effect of indexing with
                # np.where
                rsqr = np.square(np.real(data[0]))
                rsqr[np.where(data[1] == 0)] = 0
                rms_array[:, t, spw, f, pol] = np.sum(np.reshape(np.sqrt(np.sum(
                    rsqr, axis=(1, 2, 3)) / (data[0][np.where(data[1] == 0)].size - 1)), (Nbls, args.times)), axis=1)
                nsample_array[:, t, spw, f, pol] = data[
                    0][np.where(data[1] == 0)].size / Nbls
                time_array[t] = data[2]
                rms_array[nsample_array == 0] = None
                freq_array[f] = data[3]
                lst_array[t] = data[4]
                if first_time is True:
                    # add debugging code here (like print statements)
                    first_time = False
np.savez(args.out, rms_array=rms_array, nsample_array=nsample_array, header=header, time_array=time_array,
         freq_array=freq_array, baseline_array=baseline_array, spw_array=spw_array, polarization_array=polarization_array, lst_array=lst_array)
