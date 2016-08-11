# noise.py - Python utilities for noise assesment in radio telescope arrays
This code includes various tools for assessing the noise in radio telescope arrays.  Currently, this includes utilities to split data into "even" and "odd" components along the frequency, time, and polarization axis.  Subtracting neighboring elements (or matrix-subtracting "even" and "odd" datasets) is a common method of isolating noise from signals.  The code is built around pyuvdata - see [http://github.com/HERA-Team/pyuvdata].
## Getting started
This code is dependent only on pyuvdata, but the dependencies of pyubdata are not particularly well documented.  It is best to start by creating a python virtual environment.  install_requirements.sh may work as a template for an install script, but is dependent on local copies of pyuvdata and aipy.  It's probably best to just install things manually.
In a python virtualenv:
```bash
easy_install -U setuptools
pip install numpy
pip install scipy pyephem pyfits astropy
```
Install aipy from pypi:
```bash
wget https://pypi.python.org/packages/70/ef/00f6c10acceb695dae6b917b2f9e393c37a289ff6ff9c342e85e6fd57627/aipy-2.1.0.tar.gz#md5=bea343f33fc334964e634af0549a7c61
tar -xzf aipy-2.1.0.tar.gz
cd aipy-2.1.0
python setup.py install
```
If you recieve compiler errors related that look like [this](https://github.com/AaronParsons/aipy/issues/8):
```
error: format not a string literal and no format arguments [-Werror=format-security]
         PyErr_Format(PyExc_RuntimeError, e.get_message());
```
You may need to do some simple fixes to the alm_wrap.cpp, healpix_wrap.cpp, and miriad_wrap.cpp.  For each of those files, find anything that looks like:
```c++
PyErr_Format(PyExc_RuntimeError, e.get_message());
```
or
```c++
PyErr_Format(PyExc_RuntimeError, e.what());
```
and add a third argument specifying that e.*() is a string, e.g.:
```c++
PyErr_Format(PyExc_RuntimeError, "%s", e.get_message());
```
Lastly, install pyuvdata:
```bash
git clone http://github.com/HERA-Team/pyuvdata.git
cd pyuvdata
python setup.py install
```
