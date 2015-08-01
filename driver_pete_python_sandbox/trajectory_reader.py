import os
from StringIO import StringIO
from gzip import GzipFile
import numpy as np
from matplotlib.dates import date2num, num2date
import dateutil


def read_compressed_trajectory(filename):
    '''
    Compressed file with entries like:
    27-7-2015_08-01-58 32.943224 -117.220491
    '''
    filename = os.path.expanduser(filename)
    with open(filename, 'rb') as f:
        content = f.read()
        
    d = GzipFile(fileobj=StringIO(content))

    uncompressed_stream = StringIO(d.read())
    
    def _date_converter(date):
        '''
        Date has to be in this format: 27-07-2015 09:54:12
        or 2015-07-27 09:54:12
        '''
        d, t = date.split('_')
        t = t.replace('-', ':')
        result = ' '.join([d, t])
        dt = dateutil.parser.parse(result)
        return date2num(dt)
    
    print(uncompressed_stream.read())
    return np.loadtxt(uncompressed_stream,
                      converters={0: _date_converter})


def write_compressed_trajectory(trajectory, filename):
 

if __name__ == "__main__":
    trajectory = read_compressed_trajectory(os.path.expanduser("~/Downloads/trajectory.dp"))
    print(trajectory)
