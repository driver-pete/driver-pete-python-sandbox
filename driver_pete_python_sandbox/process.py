
import os

import cv2
from driver_pete_python_sandbox.filter_gps import extract_delta_time, compute_velocities, \
    extract_delta_dist, delta_float_time

from driver_pete_python_sandbox.gmaps import get_static_google_map, \
    trajectory_point_to_str, show_path
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
import matplotlib.pyplot as plots
import numpy as np
from driver_pete_python_sandbox.filter_gps_processor import filter_gps_data
from driver_pete_python_sandbox.find_enpoints import find_endpoints
from driver_pete_python_sandbox.find_routes import find_routes
from matplotlib.dates import num2date
from driver_pete_python_sandbox.utilities import ms_to_mph


def plot_velocity_histogram(data):
    delta_time = extract_delta_time(data) 
    velocities = compute_velocities(data)
    plots.plot(delta_time)
    plots.show()

    plots.hist(velocities*ms_to_mph, 100)
    plots.show()


class Path(object):
    def __init__(self, data):
        self.data = data

    def get_duration(self):
        return delta_float_time(self.data[0, 0], self.data[-1, 0])
    
    def start_time(self):
        return num2date(self.data[0][0])

    def show(self, name='path'):
        show_path(self.data, name)


def process_gps_data(filename):
    #stationary_distance_threshold=120
    # clean up data
    data = read_compressed_trajectory(filename)
    print("Length of data: %d" % len(data))
    
    data = filter_gps_data(data, stationary_distance_threshold=100)
    print("Length of filtered data: %d" % len(data))
    
    for i in range(0, 100):
        print(trajectory_point_to_str(data, i, with_address=False))

    #data = data[525:533]



    endpoints = find_endpoints(data)
    print("Found %d endpoints:" % len(endpoints))
    for u in endpoints:
        print(trajectory_point_to_str([u], 0))
    
    assert(len(endpoints) == 2)
    #data = data[:130]
    #Path(data).show()
    AtoB_paths_data, BtoA_paths_data = find_routes(data, endpoints, verbose=False)
    
    def _extract_indices(data, paths):
        result = []
        for p in paths:
            indices = [(data[:, 0] == p[0, 0]).nonzero()[0][0],
                       (data[:, 0] == p[p.shape[0]-1, 0]).nonzero()[0][0]]
            result.append(indices)
        return result

    AtoB_paths_indices = _extract_indices(data, AtoB_paths_data)
    BtoA_paths_indices = _extract_indices(data, BtoA_paths_data)

    print(AtoB_paths_indices)
    print(BtoA_paths_indices)
    
    AtoB_paths = [Path(d) for d in AtoB_paths_data]
    BtoA_paths = [Path(d) for d in BtoA_paths_data]
    
    AtoB_paths = sorted(AtoB_paths, key=lambda x: x.get_duration())
    BtoA_paths = sorted(BtoA_paths, key=lambda x: x.get_duration())

#     print("ATOB")
#     for p in AtoB_paths:
#         print(p.get_duration()/60, str(p.start_time()))
#         p.show(str(p.get_duration()/60))

    print("BTOA")
    for p in BtoA_paths:
        print(p.get_duration()/60, str(p.start_time()))
        p.show(str(p.get_duration()/60))


if __name__ == '__main__':
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    process_gps_data(os.path.join(artifacts, 'merged'))
