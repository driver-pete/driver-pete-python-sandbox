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
    result = np.delete(data, np.where(delta_time < 1.)[0] + 1, axis=0)
    print("Removed %d duplicate points." % (len(data) - len(result)))
    return result


def remove_stationary_points(data, distance_threshold=1.):
    '''
    If coordinates are not changing, there is no need to keep the record because
    timestamp can always show how long did we spend at that place
    distance_threshold - which points consider to be close
    '''
    delta_dist = extract_delta_dist(data)
    result = np.delete(data, np.where(delta_dist < distance_threshold)[0] + 1, axis=0)
    print("Removed %d stationary points." % (len(data) - len(result)))
    return result


def are_points_close(data, index1, index2, distance):
    # predicate to determine if two points are close based on index in the trajectory
    return vincenty(data[index1][1:], data[index2][1:]).meters < distance
