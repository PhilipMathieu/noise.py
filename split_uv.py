# Python script to split a pyuvdata UVData() object into odd and even portions,
# allowing differencing for applications such as noise assessment.
# This script specifically facilitates batch processing of multiple data files.
# Author: Philip Mathieu
# 8/9/2016

import os
from uvdata.uv import UVData
import noise


def splitAll(inpath, outdir, indir=False):
    # automatically process a directory if asked
    if indir:
        inpath = [x[0] for x in os.walk(inpath)]
        inpath = inpath[1:]
    # allow sting inputs as well as lists of strings
    elif not isinstance(inpath, list):
        inpath = [inpath]
    inpath.sort()
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
        print "Splitting " + path
        # process splits
        fsplits = noise.splitByFreq(uv, mode='all')
        if isinstance(fsplits, list):
            if not os.path.exists(outdir + 'fsplits/'):
                os.makedirs(outdir + 'fsplits/')
            fsplits[0].write_miriad(outdir + 'fsplits/' + path + 'O')
            fsplits[1].write_miriad(outdir + 'fsplits/' + path + 'E')
            fsplits[2].write_miriad(outdir + 'fsplits/' + path + 'D')
        else:
            print "Skipping frequency split..."
        psplits = noise.splitByPol(uv, mode='all')
        if isinstance(psplits, list):
            if not os.path.exists(outdir + 'psplits/'):
                os.makedirs(outdir + 'psplits/')
            psplits[0].write_miriad(outdir + 'psplits/' + path + 'O')
            psplits[1].write_miriad(outdir + 'psplits/' + path + 'E')
            psplits[2].write_miriad(outdir + 'psplits/' + path + 'D')
        else:
            print "Skipping polarization split..."
        tsplits = noise.splitByTime(uv, mode='all')
        if isinstance(tsplits, list):
            if not os.path.exists(outdir + 'tsplits/'):
                os.makedirs(outdir + 'tsplits/')
            tsplits[0].write_miriad(outdir + 'tsplits/' + path + 'O')
            tsplits[1].write_miriad(outdir + 'tsplits/' + path + 'E')
            tsplits[2].write_miriad(outdir + 'tsplits/' + path + 'D')
        else:
            print "Skipping time split..."
        # this may not be necessary
        del fsplits
        del psplits
        del tsplits
        del uv
    return True
