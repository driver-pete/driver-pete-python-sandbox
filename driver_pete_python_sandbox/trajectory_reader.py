import os
from StringIO import StringIO
import gzip
import numpy as np
from matplotlib.dates import date2num, num2date
import dateutil


def date_str_to_num_converter(date):
    '''
    Incoming date is in the format with the day first:
    27-7-2015_08-01-58_PDT
    
    Dateutil expects date in 27-07-2015 09:54:12 PDT
    or 2015-07-27 09:54:12 PDT format
    '''
    d, t, z = date.split('_')
    t = t.replace('-', ':')
    result = ' '.join([d, t, z])
    dt = dateutil.parser.parse(result, dayfirst=True)
    return date2num(dt)


def num_to_date_str_converter(num):
    date = num2date(num)
    # convert date to local machine timezone
    current_zone = dateutil.tz.tzlocal()
    date = date.astimezone(current_zone)
    return date.strftime("%d-%m-%Y_%H-%M-%S_%Z")
    

def read_compressed_trajectory(filename):
    '''
    Compressed file with entries like:
    27-7-2015_08-01-58 32.943224 -117.220491
    '''
    filename = os.path.expanduser(filename)
    with open(filename, 'rb') as f:
        content = f.read()
        
    d = gzip.GzipFile(fileobj=StringIO(content))

    uncompressed_stream = StringIO(d.read())
    
    return np.loadtxt(uncompressed_stream,
                      converters={0: date_str_to_num_converter})


def write_compressed_trajectory(trajectory, filename):
    filename = os.path.expanduser(filename)
    with gzip.open(filename, 'w') as f:
        for l in trajectory:    
            str_line = "%s %3.6f %3.6f\n" % (num_to_date_str_converter(l[0]), l[1], l[2])
            f.write(str_line)


if __name__ == "__main__":
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts', 'raw')
    data = read_compressed_trajectory(os.path.join(artifacts, '12-08-2015_09-31-53_PDT'))
