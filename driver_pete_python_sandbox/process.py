
import os

import cv2
from driver_pete_python_sandbox.filter_gps import extract_delta_time, compute_velocities, \
    ms_to_mph, filter_gps_data, extract_delta_dist, delta_float_time, \
    remove_stationary_points
from driver_pete_python_sandbox.find_enpoints_procedural import find_endpoints
from driver_pete_python_sandbox.find_routes_procedural import find_routes
from driver_pete_python_sandbox.gmaps import get_static_google_map, \
    trajectory_point_to_str, show_path
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
import matplotlib.pyplot as plots
import numpy as np


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
        print(trajectory_point_to_str(data, u))

    AtoB_paths, BtoA_paths = find_routes(data, endpoints, verbose=False)
    print(AtoB_paths)
    print(BtoA_paths)

    print("ATOB")
    for p in AtoB_paths:
        print(delta_float_time(data[p[0], 0], data[p[1], 0])/60)

    print("BTOA")
    for p in BtoA_paths:
        print(delta_float_time(data[p[0], 0], data[p[1], 0])/60)

    '''
    [[77, 265], [438, 608], [779, 946], [1126, 1277]]
    [[270, 435], [608, 775], [949, 1124], [1426, 1595]]
    ATOB
    26.1333333333
    15.8166666667
    15.8166666667
    15.9166666667
    BTOA
    16.5833333333
    611.383333333
    20.8166666667
    334.8
    '''
    show_path(data, AtoB_paths[6])
    # show_path(data, BtoA_paths[0])
    path_indices = AtoB_paths[1]
    path = data[path_indices[0]:path_indices[1]+1, :]
   
    for i in range(10, 20):
        print(trajectory_point_to_str(path, i)) 
    print('--------------')
#     for i in range(len(path) - 5, len(path)):
#         print(trajectory_point_to_str(path, i))
    

if __name__ == '__main__':
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    process_gps_data(os.path.join(artifacts, 'merged'))
