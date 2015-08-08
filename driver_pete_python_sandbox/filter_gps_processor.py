# ============================================================================
# Copyright 2014 BRAIN Corporation. All rights reserved. This software is
# provided to you under BRAIN Corporation's Beta License Agreement and
# your use of the software is governed by the terms of that Beta License
# Agreement, found at http://www.braincorporation.com/betalicense.
# ============================================================================


from geopy.distance import vincenty
from driver_pete_python_sandbox.filter_gps import delta_float_time, ms_to_mph
import numpy as np
from driver_pete_python_sandbox.gmaps import trajectory_point_to_str


class DuplicateTimeFilter(object):
    '''
    implements remove_duplicate_points
    '''
    def allow(self, current_p, next_p):
        dt = delta_float_time(current_p[0], next_p[0])
        return dt >= 1


class StationaryPointsFilter(object):
    '''
    implements remove_stationary_points
    '''
    def __init__(self, distance_threshold=1.):
        self._stationary_distance_threshold = distance_threshold
    
    def allow(self, current_p, next_p):
        dist = vincenty(current_p[1:], next_p[1:]).meters
        return dist >= self._stationary_distance_threshold


class VelocityOutliersFilter(object):
    '''
    remove_outliers
    '''
    def __init__(self, speed_mph_thershold=85.):
        self._threshold = speed_mph_thershold
    
    def allow(self, current_p, next_p):
        dist = vincenty(current_p[1:], next_p[1:]).meters
        dt = delta_float_time(current_p[0], next_p[0])
        v = ms_to_mph*dist/dt
        print(v, dt, dist, trajectory_point_to_str([current_p], 0), trajectory_point_to_str([next_p], 0))
        return v <= self._threshold


def apply_filter(data, afilter):
    prev_point = data[0]
    result = [prev_point]
    for i in range(1, data.shape[0]):
        if afilter.allow(prev_point, data[i]):
            prev_point = data[i]
            result.append(data[i])
        else:
            print('filter', i)
    return np.array(result)
