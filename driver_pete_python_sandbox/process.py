

import numpy as np
import matplotlib.pyplot as plots
import os
from matplotlib.dates import datestr2num, num2date
import urllib
import cv2
from geopy.distance import vincenty
from driver_pete_python_sandbox.filter_gps import extract_delta_time, compute_velocities, \
    ms_to_mph, filter_gps_data, extract_delta_dist, delta_float_time
import cPickle
from geopy.distance import vincenty
from driver_pete_python_sandbox.gmaps import get_static_google_map

from geopy.geocoders import GoogleV3 as Geocoder
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory


def process_gps_data(filename):
    
    data = filter_gps_data(read_compressed_trajectory(filename))

    delta_time = extract_delta_time(data) 
    stationary_points = np.where(delta_time>60*15)[0]
    stationary_points = [0] + list(stationary_points) + [data.shape[0]-1]
    print(stationary_points)
    
    is_close = lambda p1, p2: vincenty(p1, p2).meters < 1000
    is_index_close = lambda index1, index2: is_close(data[index1][1:], data[index2][1:])

    unique_locations = [0]
    for s in stationary_points:
        if next((u for u in unique_locations
                 if is_index_close(s, u)), None) is None:
            unique_locations.append(s)
 
    geocoder = Geocoder()
    for u in unique_locations:
        request = "%s, %s" % tuple(data[u][1:])
        print(request, geocoder.reverse(request, exactly_one = True).address)
    print(unique_locations)

    candidate_paths = [[stationary_points[i], stationary_points[i+1]]
                       for i in range(len(stationary_points)-1)]
    paths = [p for p in candidate_paths if not is_index_close(*p)]
    
    times = [delta_float_time(data[p[0]+1][0], data[p[1]][0])/60 for p in paths]

    print(paths)
    print(times)
    

    velocities = compute_velocities(data)
    plots.plot(delta_time)
    #plots.show()

    plots.hist(velocities*ms_to_mph, 100)
    #plots.show()
    
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
    process_gps_data("~/Downloads/trajectory.dp")

