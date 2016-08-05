# Code to evaluate noise in pyuvdata object by subtracting neighbboring frequencies
from uvdata.uv import UVData
import argparse
import os
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('mir', help='Path of input Miriad file')
args = parser.parse_args()

uv = UVData()
print "Reading " + args.mir
uv.read_miriad(args.mir)
print "File read."
uv.data_array_odd = uv.data_array[:,:,0::2,:]
uv.flag_array_odd = uv.flag_array[:,:,0::2,:]
# omit extra data point if present
if uv.Nfreqs % 2 == 1:
	uv.data_array_odd = uv.data_array_odd[:,:,:-1,:]
	uv.flag_array_odd = uv.flag_array_odd[:,:,:-1,:]
uv.data_array_even = uv.data_array[:,:,1::2,:]
uv.data_array_diff = uv.data_array_odd - uv.data_array_even
print "Data differenced."
uv.nsample_array = uv.nsample_array[:,:,1::2,:]
uv.flag_array = np.logical_or(uv.flag_array_odd,uv.flag_array[:,:,1::2,:])
print "Flags extended."
uv.freq_array = uv.freq_array[:,1::2]
uv.Nfreqs = uv.Nfreqs/2
uv.data_array = uv.data_array_diff
print "Writing..."
uv.write_uvfits(args.mir+'N',True,True)
