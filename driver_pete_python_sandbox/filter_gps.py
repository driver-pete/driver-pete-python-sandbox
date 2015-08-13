# ============================================================================
# Copyright 2014 BRAIN Corporation. All rights reserved. This software is
# provided to you under BRAIN Corporation's Beta License Agreement and
# your use of the software is governed by the terms of that Beta License
# Agreement, found at http://www.braincorporation.com/betalicense.
# ============================================================================


import numpy as np
import os
from driver_pete_python_sandbox.utilities import delta_float_time, distance


def extract_delta_time(data):
    '''
    Creates array of delta times between points in seconds
    '''
    times, coordinates = data[:, 0], data[:, 1:]
    return np.array([delta_float_time(times[i], times[i+1])
                     for i in range(len(times)-1)])
    

def extract_delta_dist(data):
    return np.array([distance(data[i+1], data[i])
                     for i in range(data.shape[0]-1)])
    

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
