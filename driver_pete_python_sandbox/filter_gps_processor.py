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
        if dt < 1:
            print('duplicate time')
            return False
        return True


class StationaryPointsFilter(object):
    '''
    implements remove_stationary_points
    '''
    def __init__(self, distance_threshold=1.):
        self._stationary_distance_threshold = distance_threshold
    
    def allow(self, current_p, next_p):
        dist = vincenty(current_p[1:], next_p[1:]).meters
        if dist < self._stationary_distance_threshold:
            print('duplicate position')
            return False
        return True


class VelocityOutliersFilter(object):
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
    
    Additionaly there might be large noise during imprecise stationary position.
    In this case measurements might come rarely but with huge noise (157km):
    ... SAN DIEGO
    22:30 - SAN DIEGO
    00:30 - LA
    00:33 - SAN DIEGO
    09:18 - LA
    09:19 - SAN DIEGO
    ... SAN DIEGO
    Time difference between samples is large enough to make velocity small. Moreover it is not obvious that it is
    noise at first - maybe a driver really drove to LA without taking measurements? However only later it becomes clear
    that LA measurements are noise.
    Algorithm takes preventive steps and ignores point that is too far from the previous one. This leads to a problem
    that if algorithm starts from the LA, it will never converge back to SD. Therefore there is a counter that doesn't
    allow algorithm to dismiss too many outliers in a row (there are not outliers in this case).
    '''
    def __init__(self, speed_mph_thershold=85., distance_threshold=5000.):
        self._speed_threshold = speed_mph_thershold
        self._distance_threshold = distance_threshold
        
        self._max_number_outliers = 3
        self._outliers_counter = self._max_number_outliers
    
    def allow(self, current_p, next_p):
        dist = vincenty(current_p[1:], next_p[1:]).meters
        dt = delta_float_time(current_p[0], next_p[0])
        v = ms_to_mph*dist/dt
        if v > self._speed_threshold:
            print('large speed')
            if self._outliers_counter > 0:
                self._outliers_counter -= 1
                return False
  
        if dist > self._distance_threshold:
            print('large distance')
            if self._outliers_counter > 0:
                self._outliers_counter -= 1
                return False
        self._outliers_counter = self._max_number_outliers
        return True

    def get_state(self):
        return self._outliers_counter

    def set_state(self, state):
        self._outliers_counter = state


class FilterChain(object):
    def __init__(self, chain):
        self._chain = chain

    def allow(self, current_p, next_p):
        for f in self._chain:
            if not f.allow(current_p, next_p):
                return False
        return True


def apply_filter(data, afilter):
    prev_point = data[0]
    result = [prev_point]
    for i in range(1, data.shape[0]):
        if afilter.allow(prev_point, data[i]):
            prev_point = data[i]
            result.append(data[i])

    return np.array(result)


def filter_gps_data(data, speed_mph_thershold=85, stationary_distance_threshold=1.):
    filter = FilterChain([DuplicateTimeFilter(),
                          StationaryPointsFilter(stationary_distance_threshold),
                          VelocityOutliersFilter(speed_mph_thershold)])
    return apply_filter(data, filter)
