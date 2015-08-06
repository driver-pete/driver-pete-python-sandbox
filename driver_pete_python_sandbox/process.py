

import numpy as np
import matplotlib.pyplot as plots
import os
from matplotlib.dates import datestr2num, num2date
import urllib
import cv2
from geopy.distance import vincenty
from driver_pete_python_sandbox.filter_gps import extract_delta_time, compute_velocities, \
    ms_to_mph, filter_gps_data, extract_delta_dist, delta_float_time,\
    remove_stationary_points
import cPickle
from driver_pete_python_sandbox.gmaps import get_static_google_map

from geopy.geocoders import GoogleV3 as Geocoder
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory


def trajectory_point_to_str(data, index):
    geocoder = Geocoder()
    request = "%s, %s" % tuple(data[index][1:])
    address = geocoder.reverse(request, exactly_one = True).address
    date = num2date(data[index][0])
    try:
        duration = num2date(data[index+1][0]) - date
    except IndexError:
        duration = "NO DATA"
    return "Index:%s; Date:%s; Address:%s; Coords: %s; Duration:%s;" % \
            (index, date, request, address, duration)


def are_points_close(data, index1, index2, distance):
    # predicate to determine if two points are close based on index in the trajectory
    return vincenty(data[index1][1:], data[index2][1:]).meters < distance
    

def find_endpoints(data):
    # get delta time array in seconds
    delta_time = extract_delta_time(data) 

    # get indices on the trajectory where we spend a lot of time still
    stationary_threshold = (60*60) * 3  # hours
    stationary_points = np.where(delta_time>stationary_threshold)[0]
    stationary_points = [0] + list(stationary_points) + [data.shape[0]-1]
    
    # filter out stationary points that are driving-distance (1km) close to each other
    is_index_close = lambda index1, index2: are_points_close(data, index1, index2, 1000)

    unique_locations = [stationary_points[0]]
    for s in stationary_points:
        candidates = [u for u in unique_locations
                      if is_index_close(s, u)]
        # location is unique if no candidates found
        if len(candidates) == 0:
            unique_locations.append(s)

    return unique_locations


def plot_velocity_histogram(data):
    delta_time = extract_delta_time(data) 
    velocities = compute_velocities(data)
    plots.plot(delta_time)
    plots.show()

    plots.hist(velocities*ms_to_mph, 100)
    plots.show()


def show_path(data, path_indices):
    path = data[path_indices[0]:path_indices[1]+1, :]
    times, coordinates = path[:, 0], path[:, 1:]
    
    center = np.average(coordinates, axis=0)
 
    max_markers = 64
    for i in range(len(coordinates)/max_markers + 1):
        imgdata = get_static_google_map(#center=center,
                                        #zoom=11,
                                        markers=coordinates[i*max_markers:(i+1)*max_markers])
     
        cv2.imshow(str(i), imgdata)
    cv2.waitKey()
     
    plots.plot(coordinates[:,0], coordinates[:,1], 'ro')
    plots.show()


def find_routes(data, endpoints, verbose=False):
    assert(len(endpoints) == 2)
    current_startpoint_index = 0
    current_startpoint = endpoints[current_startpoint_index]
    current_endpoint = endpoints[current_startpoint_index-1]
    AtoB_paths = []
    BtoA_paths = []
    current_path = [current_startpoint, None]
    route_started = False
    if verbose:
        print("Staring from %s" % trajectory_point_to_str(data, current_startpoint))
    distance_to_start_route = 200
    stationary_threshold = (60*60) * 3  # hours
    for i in range(current_startpoint, len(data)):
        if not route_started:
            current_path[0] = i
            if are_points_close(data, current_startpoint, i, distance_to_start_route):
                if verbose:
                    print("Haven't gone far: %s" % trajectory_point_to_str(data, i))
            else:
                route_started = True
                if verbose:
                    print("Ok, started route: %s" % trajectory_point_to_str(data, i))
        else:
            if are_points_close(data, current_endpoint, i, distance_to_start_route):
                # route acomplished:
                current_path[1] = i
                
                if current_startpoint_index % 2 == 0:
                    AtoB_paths.append(current_path)
                    if verbose:
                        print("Route A to B from %s to %s found." % (trajectory_point_to_str(data, current_path[0]),
                                                                     trajectory_point_to_str(data, current_path[1])))
                else:
                    BtoA_paths.append(current_path)
                    if verbose:
                        print("Route B to A from %s to %s found." % (trajectory_point_to_str(data, current_path[0]),
                                                                     trajectory_point_to_str(data, current_path[1])))
                
                current_startpoint_index = (current_startpoint_index + 1) % 2
                current_startpoint = endpoints[current_startpoint_index]
                current_endpoint = endpoints[current_startpoint_index-1]
                current_path = [i, None]
                route_started = False
                if verbose:
                    print("Staring from %s" % trajectory_point_to_str(data, i))
            elif are_points_close(data, current_startpoint, i, distance_to_start_route):
                # we made a loop
                if verbose:
                    print("Made a loop from %s to %s" % (trajectory_point_to_str(data, current_path[0]),
                                                         trajectory_point_to_str(data, i)))
                current_path = [i, None]
                route_started = False
                if verbose:
                    print("Staring from %s" % trajectory_point_to_str(data, i))
            elif delta_float_time(data[i-1, 0], data[i, 0]) > stationary_threshold:
                # we made a loop
                if verbose:
                    print("Ignore stationary point %s" % (trajectory_point_to_str(data, i-1),))
                current_path = [i, None]
                route_started = False
                if verbose:
                    print("Staring from %s" % trajectory_point_to_str(data, i))
         
    return AtoB_paths, BtoA_paths
    

def process_gps_data(filename):
    # clean up data
    data = filter_gps_data(read_compressed_trajectory(filename))
    print("Length of data: %d" % len(data)) 
    
    # merge points which are closer than 50m 
    data = remove_stationary_points(data, distance_threshold=50)

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
    #show_path(data, BtoA_paths[0])
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

