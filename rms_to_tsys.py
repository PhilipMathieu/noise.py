import numpy as np
from aipy.miriad import bl2ij
from tqdm import trange


def apply_gains(data, gains):
    rms = data['rms_array']
    a1 = np.ndarray(rms.shape)
    a2 = np.ndarray(rms.shape)
    for bl in trange(rms.shape[0]):
        for freq in range(rms.shape[3]):
            for pol in range(rms.shape[4]):
                (i1, i2) = bl2ij(bl)
                i1 = np.argmin(gains['HERA_list'] - i1)
                i2 = np.argmin(gains['HERA_list'] - i2)
                g1 = np.mean(gains['hera_gains'][pol, i1, np.argmin(np.abs(
                    gains['freqs'] - data['freq_array'][freq] / 1e6)), np.logical_and(gains['lsts'] < 11, gains['lsts'] > 6)])
                g2 = np.mean(gains['hera_gains'][pol, i2, np.argmin(np.abs(
                    gains['freqs'] - data['freq_array'][freq] / 1e6)), np.logical_and(gains['lsts'] < 11, gains['lsts'] > 6)])
                a1[bl, :, 0, freq, pol] = np.tile(g1, (rms.shape[1],))
                a2[bl, :, 0, freq, pol] = np.tile(g2, (rms.shape[1],))
    tsys = np.divide(rms, np.sqrt(np.multiply(a1, a2)))
    tsys[tsys <= 0] = 0
    return tsys
