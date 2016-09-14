import matplotlib.pyplot as plt
import numpy as np
import os
from aipy.miriad import bl2ij
import fnmatch

bl2ijV = np.vectorize(bl2ij)


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


def meanvst(data, outfile):
    for spw in range(data['rms_array'].shape[2]):
        for pol in range(data['rms_array'].shape[4]):
            plt.scatter(data['time_array'], np.nanmean(np.nanmean(less_cross(data), axis=0),axis=2)[:,spw,pol])
    plt.title('Mean RMSE vs Time, All SPW and Pol')
    plt.xlabel('Time')
    plt.ylabel('Raw RMSE')
    plt.savefig(outfile, format='png', bbox='tight')
    plt.clf()


def meanvsf(data, outfile):
    for spw in range(data['rms_array'].shape[2]):
        for pol in range(data['rms_array'].shape[4]):
            plt.scatter(data['freq_array'], np.nanmean(np.nanmean(less_cross(data), axis=0),axis=0)[spw,:,pol])
    plt.title('Mean RMSE vs Frequency, All SPW and Pol')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Raw RMSE')
    plt.savefig(outfile, format='png', bbox='tight')
    plt.clf()


def meanwfall(data, outfile):
    spws = data['rms_array'].shape[2]
    pols = data['rms_array'].shape[4]
    for spw in range(spws):
        for pol in range(pols):
            plt.subplot(spws, pols, spw + 1 + (pol * spws))
            plt.imshow(
                np.nanmean(less_cross(data)[:, :, spw, :, pol], axis=0), aspect='auto', interpolation='none')
    plt.title('Mean RMSE Waterfall, All Baselines')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Time')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Raw RMSE', rotation=270)
    plt.savefig(outfile, format='png', bbox='tight')
    plt.clf()


def plot_report(data, outdir):
    base = os.getcwd()
    try:
        os.chdir(os.path.join(base, outdir))
    except:
        os.makedirs(os.path.join(base, outdir))
        os.chdir(os.path.join(base, outdir))
    meanvst(data, 'mvst.png')
    meanvsf(data, 'mvsf.png')
    meanwfall(data, 'mwf.png')
    os.chdir(base)


def less_cross(data):
    ij = bl2ijV(data['baseline_array'])
    cross = np.where(ij[0] != ij[1])
    return data['rms_array'][cross, :, :, :, :][0, :, :, :, :, :]


def batch_report(files, outdir):
    print files
    base = os.getcwd()
    if isinstance(files, str):
        try:
            datadir,regex = os.path.split(files)
            os.chdir(datadir)
            print os.getcwd()
            files = fnmatch.filter(os.listdir('./'), os.path.split(files)[1])
        except:
            print "Neither list nor valid regex provided!"
            return
    else:
        datadir = base
    try:
        os.chdir(os.path.join(base, outdir))
    except:
        os.makedirs(os.path.join(base, outdir))
        os.chdir(os.path.join(base, outdir))
    for file in files:
        print file
        data = np.load(os.path.join(base,datadir, file))
        plot_report(data, file)
    os.chdir(base)
