from uvdata.uv import UVData
import noise

uv = UVData()
uv.read_miriad('data/zen.2456865.60537.xx.uvcRREATU')
print "Finished reading"
#uvf = noise.splitByFreq(uv, mode='diff')
uvp = noise.splitByPol(uv, mode='diff')
uvt = noise.splitByTime(uv, mode='diff')
#uvf.write_uvfits('data/psasmallf')
#uvp.write_uvfits('data/psasmallp',True,False,False,False)
uvt.write_uvfits('data/psasmallt')
