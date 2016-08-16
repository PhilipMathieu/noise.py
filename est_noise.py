import numpy as np
import os
import argparse
from uvdata.uv import UVData
import math
from uvbuffer import UVBuffer


# options parser for min and max frequency and time
parser = argparse.ArgumentParser()
parser.add_argument('mir', help='Path of input Miriad file')
parser.add_argument('-d', action='store_true',
                    help="Enable directory mode.  Useful when data is distributed in a series of input files.")
parser.add_argument('-t', '--times', type=str, default="1",
                    help="Number of integrations to take RMSE over.  Defaults to 1.  Default unit is integrations - use s to specify seconds, e.g. 120s")
parser.add_argument('-f', '--freq', type=str, default="1",
                    help="Number of frequencies/channels to take RMSE over.  Defaults to 1.  Default unit is channels - use MHz to specify frequency range")
parser.add_argument('-s', '--suff', default="",
                    help="Suffix of files to process.  Helpful if directory contains
                    non - dfferenced files")

args = parser.parse_args()
# read in the filenames from the directory
if args.d:
    files = os.listdir(inpath)
    for file in files:
        if not file.endswith(args.s):
            files.remove[file]
else:
    files = args.mir
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
Nfreqs = uva.Nfreqs
Nbls = uva.Nbls
Nspws = uva.Nspws
Npols = uva.Npols
Nblts = uva.Nblts
# check input validity
Ntimes = (last_time - first_time) / integration_time
if Ntimes < args.t:
    print "Warning: fewer time samples than requested time RMSE window.  Result will be single value."
if Nfreqs < args.f:
    print "Warning: fewer frequency samples than requested frequency RMSE window.  Result will be single value."
# calculate samples to average in each dimension
tsamps = Ntimes / args.t
fsamps = Nfreqs / args.f
# instantiate arrays for storing RMSE and number of samples per RMS value
rms_array = np.ndarray((Nbls * tsamps, Nspws, fsamps, Npols))
nsample_array = np.ndarray((Nbls * tsamps, Nspws, fsamps, Npols))
# create a buffer of uvdata objects big enough to accomodate integration window
min_files = int(math.ceil(float(args.t) / float(uva.Ntimes))) + 1

# main loop
# for every position in the RMS matrix
# cursor = position of the element
# convert to theoretical range
# use next_file to figure out which files this range is contained in
# use file_index to locate these ranges in buffer
#
# Calculate an RMS, n samples (accounting for flagging)
# basically just do np.sqrt(real(uv[whatever])**2.sum()/(that.len()-1))
# increment buffer
# loop
# write out intelligently