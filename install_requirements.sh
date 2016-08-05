# this script installs the required packages in an order that makes pip happy
pip install numpy
pip install scipy pyephem pyfits astropy
pip install aipy
if [ -d '~/src/pyuvdata' ]; then
python ~/src/pyuvdata/setup.py install
fi
# pyuvdata must be installed manually if not kept in the ~/src folder
