# ============================================================================
# Copyright 2014 BRAIN Corporation. All rights reserved. This software is
# provided to you under BRAIN Corporation's Beta License Agreement and
# your use of the software is governed by the terms of that Beta License
# Agreement, found at http://www.braincorporation.com/betalicense.
# ============================================================================


import numpy as np
from matplotlib.dates import datestr2num, num2date
from geopy.distance import vincenty
import os


ms_to_mph = 2.23694
ms_to_kmh = 3.6


def delta_float_time(time_float1, time_float2):
    '''
    Returns delta time in seconds
    '''
    return (num2date(time_float2) - num2date(time_float1)).total_seconds()


def extract_delta_time(data):
    '''
    Creates array of delta times between points in seconds
    '''
    times, coordinates = data[:, 0], data[:, 1:]
    return np.array([delta_float_time(times[i], times[i+1])
                     for i in range(len(times)-1)])
    

def extract_delta_dist(data):
    times, coordinates = data[:, 0], data[:, 1:]
    return np.array([vincenty(coordinates[i+1], coordinates[i]).meters
                    for i in range(coordinates.shape[0]-1)])
    

def compute_velocities(data):
    delta_time = extract_delta_time(data)
    delta_dist = extract_delta_dist(data)
    return delta_dist/delta_time


def remove_duplicate_points(data):
    '''
    Remove gps readings made at the same time - duplicates
    '''
    delta_time = extract_delta_time(data)
    # remove all entries that has dt less than 1 second
    result = np.delete(data, np.where(delta_time < 1.)[0], axis=0)
    print("Removed %d duplicate points." % (len(data) - len(result)))
    return result


def remove_outliers_impl(data, thershold=85):
    '''
    Typical bad gps samples look like this:
    i  time     long.         lat      dt   ds      v (mph)       
    1  t1     32.994390  -117.084058  6.0  134.3   75.
    2  t2     32.994390  -117.084058  4.0  0.0     0.0
    3  t3     32.991641  -117.083729e 5.0  306.4   171.
    
    Where dt - time from the previous sample, ds - distance from the previous sample in meters,
    v - current velocity based on the current and the previous sample.
    
    These readings were taken on the freeway. There is a sample that has the same long, lat. readings
    but different time. It looks like the car did not move at t2 and then suddenly jumped to location at t3.
    This leads to huge car velocity at the next sample.
    The solution is to just remove such samples from the data based on the big velocity (>thershold).
    thershold - velocity that is considered to be too big (in mph)
    '''
    velocities = compute_velocities(data)
    outliers = np.where(velocities*ms_to_mph > 85)[0]
    return np.delete(data, outliers, axis=0)


def remove_outliers(data, thershold=85):
    '''
    see remove_outliers_impl first.
    It is probable that bad gps samples might come in sequence.
    in this case we just do several passes of removing outliers
    '''
    total_removed = 0
    while True:
        result = remove_outliers_impl(data, thershold)
        outliers_removed = (len(data) - len(result))
        total_removed += outliers_removed
        if outliers_removed == 0:
            print("Removed %d outliers." % total_removed)
            # check that there are no huge velocities left
            velocities = compute_velocities(result) 
            assert(np.amax(velocities)*ms_to_mph < thershold)
            return result
        else:
            data = result


def remove_stationary_points(data, distance_threshold):
    '''
    If coordinates are not changing, there is no need to keep the record because
    timestamp can always show how long did we spend at that place
    distance_threshold - which points consider to be close
    '''
    delta_dist = extract_delta_dist(data)
    result = np.delete(data, np.where(delta_dist < distance_threshold)[0] + 1, axis=0)
    print("Removed %d stationary points." % (len(data) - len(result)))
    return result


def filter_gps_data(data, speed_mph_thershold=85, stationary_distance_threshold=1.):
    data = remove_duplicate_points(data)
    data = remove_stationary_points(data, stationary_distance_threshold)
    data = remove_outliers(data, speed_mph_thershold)
    return data


def are_points_close(data, index1, index2, distance):
    # predicate to determine if two points are close based on index in the trajectory
    return vincenty(data[index1][1:], data[index2][1:]).meters < distance
