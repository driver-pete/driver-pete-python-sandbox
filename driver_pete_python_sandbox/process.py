
import os

import cv2
from driver_pete_python_sandbox.filter_gps import extract_delta_time, compute_velocities, \
    ms_to_mph, extract_delta_dist, delta_float_time

from driver_pete_python_sandbox.gmaps import get_static_google_map, \
    trajectory_point_to_str, show_path
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
import matplotlib.pyplot as plots
import numpy as np
from driver_pete_python_sandbox.filter_gps_processor import filter_gps_data
from driver_pete_python_sandbox.find_enpoints import find_endpoints
from driver_pete_python_sandbox.find_routes import find_routes


def plot_velocity_histogram(data):
    delta_time = extract_delta_time(data) 
    velocities = compute_velocities(data)
    plots.plot(delta_time)
    plots.show()

    plots.hist(velocities*ms_to_mph, 100)
    plots.show()


def process_gps_data(filename):
    # clean up data
    data = filter_gps_data(read_compressed_trajectory(filename))
    print("Length of data: %d" % len(data)) 

    endpoints = find_endpoints(data)
    assert(len(endpoints) == 2)
    print("Found %d endpoints:" % len(endpoints))
    for u in endpoints:
        print(trajectory_point_to_str([u], 0))

    AtoB_paths, BtoA_paths = find_routes(data, endpoints, verbose=False)
    def _extract_indices(data, paths):
        indices = []
        for p in paths:
            indices = [(data[:, 0] == p[0, 0]).nonzero()[0][0],
                       (data[:, 0] == p[p.shape[0]-1, 0]).nonzero()[0][0]]
            indices.append(indices)
        return indices

    AtoB_paths_indices = _extract_indices(data, AtoB_paths)
    BtoA_paths_indices = _extract_indices(data, BtoA_paths)

    print(AtoB_paths_indices)
    print(BtoA_paths_indices)

    print("ATOB")
    for p in AtoB_paths:
        print(delta_float_time(p[0, 0], p[-1, 0])/60)

    print("BTOA")
    for p in BtoA_paths:
        print(delta_float_time(p[0, 0], p[-1, 0])/60)

    show_path(AtoB_paths[0])
    

if __name__ == '__main__':
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    process_gps_data(os.path.join(artifacts, 'merged'))
