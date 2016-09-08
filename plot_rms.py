import matplotlib.pyplot as plt
import numpy as np


def tsys_plot(tsys, bl):
    plt.imshow(tsys[bl, :, 0, :, 0], interpolation='none')
    plt.title('T_sys Based on HERA Gains')
    plt.ylabel('Time Sample')
    plt.xlabel('Freq Channel')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('T_sys (K)', rotation=270)
    plt.show()


def raw_plot(rms, bl):
    plt.imshow(rms[bl, :, 0, :, 0], interpolation='none')
    plt.title('Raw RMSE Based on HERA Gains')
    plt.ylabel('Time Sample')
    plt.xlabel('Freq Channel')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Raw RMSE', rotation=270)
    plt.show()


def zero2None(rms):
    nanrms = np.copy(rms)
    nanrms[rms == 0] = np.nan
    return nanrms
