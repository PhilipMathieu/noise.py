from uvdata.uv import UVData
import noise

uv = UVData()
uv.read_miriad('data/psa128')
print "Finished reading"
uvf = noise.splitByFreq(uv, mode='diff')
uvp = noise.splitByPol(uv, mode='diff')
uvt = noise.splitByTime(uv, mode='diff')
uvf.write_miriad('data/psa128f')
uvp.write_miriad('data/psa128f')
uvt.write_miriad('data/psa128f')
