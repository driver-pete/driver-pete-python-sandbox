import os
from StringIO import StringIO
from gzip import GzipFile


def read_compressed_trajectory(filename):
    with open(filename, 'rb') as f:
        content = f.read()
        
    d = GzipFile(fileobj=StringIO(content)) 
    return d.read()
    

if __name__ == "__main__":
    trajectory = read_compressed_trajectory(os.path.expanduser("~/Downloads/trajectory.dp"))
    print(trajectory)
