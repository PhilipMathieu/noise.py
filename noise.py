from uvdata.uv import UVData
import argparse
import os
import numpy as np

def splitByFreq(uv,mode='all'):
    uvo = uv
    uve = uv
    # reading every other
    uvo.data_array = uv.data_array[:,:,0::2,:]
    uve.data_array = uv.data_array[:,:,1::2,:]
    uvo.flag_array = uv.flag_array[:,:,0::2,:]
    uve.flag_array = uv.flag_array[:,:,1::2,:]
    uvo.freq_array = uv.freq_array[:,0::2]
    uve.freq_array = uv.freq_array[:,1::2]
    uvo.nsample_array = uv.nsample_array[:,:,0::2,:]
    uve.nsample_array = uv.nsample_array[:,:,1::2,:]
    # omit extra data point if present
    if uv.Nfreqs % 2 == 1:
	    uvo.data_array = uvo.data_array[:,:,:-1,:]
	    uvo.flag_array = uvo.flag_array[:,:,:-1,:]
	    uvo.freq_array = uvo.freq_array[:,:-1]
	    uvo.nsample_array = uvo.nsample_array[:,:,:-1,:]
    uvo.Nfreqs = uv.Nfreqs/2
    uve.Nfreqs = uv.Nfreqs/2
    # differencing
    if mode == 'diff' or mode == 'all':
        uvd = uv
        uvd.data_array = uvo.data_array - uve.data_array
        uvd.flag_array = np.logical_or(uvo.flag_array,uve.flag_array)
        # label frequencies as the mean frequency (may not be best solution!)
        uvd.freq_array = np.mean([uvo.freq_array,uve.freq_array])
        uvd.nsample_array = uvo.nsample_array + uve.nsample_array
        uvd.Nfreqs = uv.Nfreqs/2
        if mode == 'diff':
            return uvd
        else:
            return [uvo,uve,uvd]
    elif mode == 'odd':
        return uvo
    elif mode == 'even':
        return uve
    else:
        return [uvo,uve]

def splitByPol(uv,mode='all'):
    uvo = uv
    uve = uv
    # reading every other
    uvo.data_array = uv.data_array[:,:,:,0::2]
    uve.data_array = uv.data_array[:,:,:,1::2]
    uvo.flag_array = uv.flag_array[:,:,:,0::2]
    uve.flag_array = uv.flag_array[:,:,:,1::2]
    uvo.polarization_array = uv.polarization_array[0::2]
    uve.polarization_array = uv.polarization_array[1::2]
    uvo.nsample_array = uv.nsample_array[:,:,:,0::2]
    uve.nsample_array = uv.nsample_array[:,:,:,1::2]
    # omit extra data point if present
    if uv.Npols % 2 == 1:
	    uvo.data_array = uvo.data_array[:,:,:,:-1]
	    uvo.flag_array = uvo.flag_array[:,:,:,:-1]
	    uvo.polarization_array = uvo.freq_array[:-1]
	    uvo.nsample_array = uvo.nsample_array[:,:,:,:-1]
    uvo.Npols = uv.Npols/2
    uve.Npols = uv.Npols/2
	# differencing
    if mode == 'diff' or mode == 'all':
        uvd = uv
        uvd.data_array = uvo.data_array - uve.data_array
        uvd.flag_array = np.logical_or(uvo.flag_array,uve.flag_array)
        # NEED TO FIGURE OUT WHAT TO LABEL POLARIZATIONS AS
        uvd.nsample_array = uvo.nsample_array + uve.nsample_array
        uvd.Npols = uv.Npols/2
        if mode == 'diff':
            return uvd
        else:
            return [uvo,uve,uvd]
    elif mode == 'odd':
        return uvo
    elif mode == 'even':
        return uve
    else:
        return [uvo,uve]

def splitByTime(uv,mode='all'):
    uvo = uv
    uve = uv
    # generate masks
    omask = np.ndarray((uv.Nblts,uv.Nspws,uv.Nfreqs,uv.Npols),dtype=bool)
    omask.fill(True)
    for i in range(0,Ntimes):
        if i%2==1:
            omask[i*uv.Nbls:(i+1)*uv.Nbls,:,:,:].fill(False)
    emask = np.logical_not(omask)
    if Ntimes%2==1:
        omask[-uv.Nbls:,:,:,:].fill(False)
    # reading every other
    uvo.data_array = uv.data_array[omask]
    uve.data_array = uv.data_array[emask]
    uvo.flag_array = uv.flag_array[omask]
    uve.flag_array = uv.flag_array[emask]
    uvo.nsample_array = uv.nsample_array[omask]
    uve.nsample_array = uv.nsample_array[emask]
    # omit extra data point if present
    if uv.Npols % 2 == 1:
        uvo.polarization_array = uvo.freq_array[:-1]
    uvo.Npols = uv.Npols/2
    uve.Npols = uv.Npols/2
    # differencing
    if mode == 'diff' or mode == 'all':
        uvd = uv
        uvd.data_array = uvo.data_array - uve.data_array
        uvd.flag_array = np.logical_or(uvo.flag_array,uve.flag_array)
        # NEED TO FIGURE OUT WHAT TO LABEL POLARIZATIONS AS
        uvd.nsample_array = uvo.nsample_array + uve.nsample_array
        uvd.Npols = uv.Npols/2
        if mode == 'diff':
            return uvd
        else:
            return [uvo,uve,uvd]
    elif mode == 'odd':
        return uvo
    elif mode == 'even':
        return uve
    else:
        return [uvo,uve]