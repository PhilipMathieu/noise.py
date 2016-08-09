from uvdata.uv import UVData
import noise

uv = UVData()
uv.read_miriad('data/psa128')
print "Finished reading"
uvf = noise.splitByFreq(uv, mode='diff',checks=True)
uvp = noise.splitByPol(uv, mode='diff',checks=True)
uvt = noise.splitByTime(uv, mode='diff',checks=True)
print "Now writing"
uvf.write_uvfits('data/psa128f')
uvp.write_uvfits('data/psa128p')
uvt.write_uvfits('data/psa128t')
