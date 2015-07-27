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
    return (num2date(time_float2) - num2date(time_float1)).total_seconds()


def extract_delta_time(data):
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
    return np.delete(data, np.where(delta_time < 1.)[0], axis=0)


def remove_outliers(data, thershold=85):
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

def remove_stationary_points(data):
    '''
    If coordinates are not changing, there is no need to keep the record because
    timestamp can always show how long did we spend at that place
    '''
    delta_dist = extract_delta_dist(data)
    return np.delete(data, np.where(delta_dist < 1.)[0] + 1, axis=0)


def filter_gps_data(data, thershold=85):
    data = remove_duplicate_points(data)
    data = remove_stationary_points(data)
    # it is probable that bad gps samples might come in sequence.
    # in this case we just do several passes of removing outliers
    for i in range(3):
        data = remove_outliers(data, thershold)
    
    # check that there are no huge velocities left
    velocities = compute_velocities(data) 
    assert(np.amax(velocities)*ms_to_mph < thershold)
    return data