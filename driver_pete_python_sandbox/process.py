

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


def find_endpoints(data):
    # get delta time array in seconds
    delta_time = extract_delta_time(data) 

    # get indices on the trajectory where we spend a lot of time still
    stationary_threshold = (60*60) * 3  # hours
    stationary_points = np.where(delta_time>stationary_threshold)[0]
    stationary_points = [0] + list(stationary_points) + [data.shape[0]-1]
    
    print("Found %d stationary points:" % (len(stationary_points)))
    for p in stationary_points:
        print(trajectory_point_to_str(data, p))

    # filter out stationary points that are driving-distance (2km) close to each other
    is_close = lambda p1, p2: vincenty(p1, p2).meters < 1000
    # predicate to determine if two points are close based on index in the trajectory
    is_index_close = lambda index1, index2: is_close(data[index1][1:], data[index2][1:])

    unique_locations = [stationary_points[0]]
    for s in stationary_points:
        candidates = (u for u in unique_locations
                      if is_index_close(s, u))
        if next(candidates, None) is None:
            unique_locations.append(s)

    return unique_locations
    


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

    return
    # candidate paths
    candidate_paths = [[stationary_points[i], stationary_points[i+1]]
                       for i in range(len(stationary_points)-1)]
    paths = [p for p in candidate_paths if not is_index_close(*p)]
    
    times = [delta_float_time(data[p[0]+1][0], data[p[1]][0])/60 for p in paths]

    print(paths)
    print(times)

    velocities = compute_velocities(data)
    plots.plot(delta_time)
    plots.show()

    plots.hist(velocities*ms_to_mph, 100)
    plots.show()
    
    times, coordinates = data[:, 0], data[:, 1:]
    center = np.average(coordinates, axis=0)
    print(center)

    imgdata = get_static_google_map(#center=center,
                                    #zoom=14,
                                    markers=coordinates[90:170])

    cv2.imshow('A', imgdata)
    cv2.waitKey()
    
    plots.plot(coordinates[:,0], coordinates[:,1], 'ro')
    plots.show()


if __name__ == '__main__':
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    process_gps_data(os.path.join(artifacts, 'merged'))

