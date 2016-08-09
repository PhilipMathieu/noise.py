from uvdata.uv import UVData
import numpy as np
from copy import deepcopy


def splitByFreq(uv, mode='all'):
    uvo = deepcopy(uv)
    uve = deepcopy(uv)
    # reading every other
    uvo.data_array = uv.data_array[:, :, 0::2, :]
    uve.data_array = uv.data_array[:, :, 1::2, :]
    uvo.flag_array = uv.flag_array[:, :, 0::2, :]
    uve.flag_array = uv.flag_array[:, :, 1::2, :]
    uvo.freq_array = uv.freq_array[:, 0::2]
    uve.freq_array = uv.freq_array[:, 1::2]
    uvo.nsample_array = uv.nsample_array[:, :, 0::2, :]
    uve.nsample_array = uv.nsample_array[:, :, 1::2, :]
    # omit extra data point if present
    if uv.Nfreqs % 2 == 1:
        uvo.data_array = uvo.data_array[:, :, :-1, :]
        uvo.flag_array = uvo.flag_array[:, :, :-1, :]
        uvo.freq_array = uvo.freq_array[:, :-1]
        uvo.nsample_array = uvo.nsample_array[:, :, :-1, :]
    uvo.Nfreqs = uv.Nfreqs / 2
    uve.Nfreqs = uv.Nfreqs / 2
    # differencing
    if mode == 'diff' or mode == 'all':
        uvd = deepcopy(uv)
        uvd.data_array = uvo.data_array - uve.data_array
        uvd.flag_array = np.logical_or(uvo.flag_array, uve.flag_array)
        # label frequencies as the mean frequency (may not be best solution!)
        uvd.freq_array = np.mean([uvo.freq_array, uve.freq_array])
        uvd.nsample_array = uvo.nsample_array + uve.nsample_array
        uvd.Nfreqs = uv.Nfreqs / 2
        if mode == 'diff':
            return uvd
        else:
            return [uvo, uve, uvd]
    elif mode == 'odd':
        return uvo
    elif mode == 'even':
        return uve
    else:
        return [uvo, uve]


def splitByPol(uv, mode='all'):
    uvo = deepcopy(uv)
    uve = deepcopy(uv)
    # reading every other
    uvo.data_array = uv.data_array[:, :, :, 0::2]
    uve.data_array = uv.data_array[:, :, :, 1::2]
    uvo.flag_array = uv.flag_array[:, :, :, 0::2]
    uve.flag_array = uv.flag_array[:, :, :, 1::2]
    uvo.polarization_array = uv.polarization_array[0::2]
    uve.polarization_array = uv.polarization_array[1::2]
    uvo.nsample_array = uv.nsample_array[:, :, :, 0::2]
    uve.nsample_array = uv.nsample_array[:, :, :, 1::2]
    # omit extra data point if present
    if uv.Npols % 2 == 1:
	    uvo.data_array = uvo.data_array[:,:,:,:-1]
	    uvo.flag_array = uvo.flag_array[:,:,:,:-1]
	    uvo.polarization_array = uvo.polarization_array[:-1]
	    uvo.nsample_array = uvo.nsample_array[:,:,:,:-1]
    uvo.Npols = uv.Npols/2
    uve.Npols = uv.Npols/2
	# differencing
    if mode == 'diff' or mode == 'all':
        uvd = deepcopy(uv)
        uvd.data_array = uvo.data_array - uve.data_array
        uvd.flag_array = np.logical_or(uvo.flag_array, uve.flag_array)
        # NEED TO FIGURE OUT WHAT TO LABEL POLARIZATIONS AS
        uvd.nsample_array = uvo.nsample_array + uve.nsample_array
        uvd.Npols = uv.Npols / 2
        if mode == 'diff':
            return uvd
        else:
            return [uvo, uve, uvd]
    elif mode == 'odd':
        return uvo
    elif mode == 'even':
        return uve
    else:
        return [uvo, uve]


def splitByTime(uv, mode='all'):
    uvo = deepcopy(uv)
    uve = deepcopy(uv)
    # generate masks
    omask4 = np.ndarray((uv.Nblts, uv.Nspws, uv.Nfreqs, uv.Npols), dtype=bool)
    omask4.fill(True)
    for i in range(0, uv.Ntimes):
        if i % 2 == 1:
            omask4[i * uv.Nbls:(i + 1) * uv.Nbls, :, :, :].fill(False)
    emask4 = np.logical_not(omask4)
    if uv.Ntimes % 2 == 1:
        omask4[-uv.Nbls:, :, :, :].fill(False)
    omask1 = omask4[:, 0, 0, 0]
    emask1 = emask4[:, 0, 0, 0]
    # 4-d parametersf
    for param in ['data_array', 'flag_array', 'nsample_array']:
        setattr(uvo, param, getattr(uv, param)[omask4])
        setattr(uve, param, getattr(uv, param)[emask4])
    # 2-d parameters
    for param in ['uvw_array']:
        setattr(uvo, param, getattr(uv, param)[np.tile(omask1, (3, 1))])
        setattr(uve, param, getattr(uv, param)[np.tile(emask1, (3, 1))])
    # 1-d parameters
    for param in ['time_array', 'lst_array', 'ant_1_array', 'ant_2_array', 'baseline_array']:
        setattr(uvo, param, getattr(uv, param)[omask1])
        setattr(uve, param, getattr(uv, param)[emask1])
    # scalar parameters
    uvo.Nblts = np.sum(omask1)
    uve.Nblts = np.sum(emask1)
    uvo.Ntimes = uvo.Nblts / uvo.Nbls
    uve.Ntimes = uve.Nblts / uve.Nbls
    # # tests
    # if uvo.Ntimes == uve.Ntimes:
    #     print "Ntimes correct"
    # else:
    #     print "Ntimes check failed"
    # if uvo.uvw_array.all() == uve.uvw_array.all():
    #     print "UVW arrays match"
    # else:
    #     print "UVW check failed"
    # differencing
    if mode == 'diff' or mode == 'all':
        uvd = deepcopy(uv)
        uvd.data_array = uvo.data_array - uve.data_array
        uvd.flag_array = np.logical_or(uvo.flag_array, uve.flag_array)
        uvd.nsample_array = uvo.nsample_array + uve.nsample_array
        # copy all other attributes
        for param in ['uvw_array', 'time_array', 'lst_array', 'ant_1_array', 'ant_2_array', 'baseline_array', 'Nblts', 'Ntimes']:
            setattr(uvd, param, getattr(uvo, param))
        if mode == 'diff':
            return uvd
        else:
            return [uvo, uve, uvd]
    elif mode == 'odd':
        return uvo
    elif mode == 'even':
        return uve
    else:
        return [uvo, uve]