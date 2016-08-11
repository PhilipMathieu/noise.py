import os
from uvdata.uv import UVData
import noise


def splitAll(inpath, outdir):
    # allow sting inputs as well as lists of strings
    if not isinstance(inpath, list):
        inpath = [inpath]
    for path in inpath:
        # catch read errors
        try:
            uv = UVData()
            uv.read_miriad(path)
        except:
            print "Could not read " + path + ". Is this a valid Miriad file?"
            continue
        # change path to the useful part
        path = os.path.basename(os.path.normpath(path))
        # process splits
        fsplits = noise.splitByFreq(uv, mode='all')
        if isinstance(fsplits, list):
            if not os.path.exists(outdir + 'fsplits/'):
                os.makedirs(outdir + 'fsplits/')
            fsplits[0].write_miriad(outdir + 'fsplits/' + path + '.odd')
            fsplits[1].write_miriad(outdir + 'fsplits/' + path + '.even')
            fsplits[2].write_miriad(outdir + 'fsplits/' + path + '.diff')
        else:
            print "Skipping frequency split..."
        psplits = noise.splitByPol(uv, mode='all')
        if isinstance(psplits, list):
            if not os.path.exists(outdir + 'psplits/'):
                os.makedirs(outdir + 'psplits/')
            psplits[0].write_miriad(outdir + 'psplits/' + path + '.odd')
            psplits[1].write_miriad(outdir + 'psplits/' + path + '.even')
            psplits[2].write_miriad(outdir + 'psplits/' + path + '.diff')
        else:
            print "Skipping polarization split..."
        tsplits = noise.splitByTime(uv, mode='all')
        if isinstance(tsplits, list):
            if not os.path.exists(outdir + 'tsplits/'):
                os.makedirs(outdir + 'tsplits/')
            tsplits[0].write_miriad(outdir + 'tsplits/' + path + '.odd')
            tsplits[1].write_miriad(outdir + 'tsplits/' + path + '.even')
            tsplits[2].write_miriad(outdir + 'tsplits/' + path + '.diff')
        else:
            print "Skipping time split..."
        del fsplits
        del psplits
        del tsplits
        del uv
    return True
