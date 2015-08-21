# ============================================================================
# Copyright 2014 BRAIN Corporation. All rights reserved. This software is
# provided to you under BRAIN Corporation's Beta License Agreement and
# your use of the software is governed by the terms of that Beta License
# Agreement, found at http://www.braincorporation.com/betalicense.
# ============================================================================


import pprint
import tempfile

from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.filter_gps import compute_velocities, \
    remove_duplicate_points, \
    extract_delta_time, extract_delta_dist, remove_stationary_points
from driver_pete_python_sandbox.filter_gps_processor import apply_filter, \
    DuplicateTimeFilter, VelocityOutliersFilter, filter_gps_data
from driver_pete_python_sandbox.gmaps import trajectory_point_to_str
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
import numpy as np
from driver_pete_python_sandbox.utilities import distance, ms_to_mph


def _get_test_data():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_raw_0", folder)
    data = read_compressed_trajectory(filename)
    # add few time duplicates
    data[54] = data[53]
    data[100] = data[99]
    
    # add few distance duplicates
    data[23][1:] = data[22][1:]
    data[40][1:] = data[39][1:]
    data[60][1:] = data[59][1:]
    return data
 
 
def test_remove_duplicate_readings():
    data = _get_test_data()
    velocities = compute_velocities(data)
    number_of_duplicates = np.sum(np.isnan(velocities))
     
    fixed_data = remove_duplicate_points(data)
    fixed_velocities = compute_velocities(fixed_data)
    assert(np.sum(np.isnan(fixed_velocities)) == 0)
    # check that we deleted duplicates only
    print(data.shape[0])
    print(fixed_data.shape[0])
    print(number_of_duplicates)
    assert(fixed_data.shape[0] == data.shape[0] - number_of_duplicates)
    print(fixed_data.shape[0], data.shape[0])
    
    fixed_data_processor = apply_filter(data, DuplicateTimeFilter())
    assert((fixed_data == fixed_data_processor).all())
    
 
def test_remove_outliers():
    np.set_printoptions(suppress=True)
    data = remove_stationary_points(remove_duplicate_points(_get_test_data()))
 
    velocity_threshold = 85.
    fixed_data = apply_filter(data, VelocityOutliersFilter(velocity_threshold))
    
    # check that data has outliers in velocity and distance
    velocities = compute_velocities(data)
    outliers = np.where(velocities*ms_to_mph > 85)[0]
    assert(len(outliers)>0)
    assert(np.amax(extract_delta_dist(data)) > 157900)

    # no large velocities left
    velocities = compute_velocities(fixed_data) 
    assert(np.amax(velocities)*ms_to_mph < velocity_threshold)
    assert(np.amax(extract_delta_dist(fixed_data)) < 330)
    
    # we expect 5 point to be removed
    assert(data.shape[0] - fixed_data.shape[0] == 5)


def test_remove_stationary_noise():
    '''
    The data has large amount of noise - switching between SD and LA every 10 seconds.
    It starts from SD, then noise, later it returns to SD. We test that LA is ignored
    '''
    data = remove_duplicate_points(_get_test_data())[561:576]

    fixed_data = apply_filter(data, VelocityOutliersFilter(85))
    assert(len(fixed_data) == 11)
    
    stationary_point = [0, 33.004964, -117.060207]
    distances = np.array([distance(stationary_point, d)
                          for d in fixed_data])
    
    assert((distances < 246.6).all())


def test_remove_stationary_noise_return_to_stable():
    '''
    The data has large amount of noise - switching between SD and LA every 10 seconds.
    It starts from the noisy point, later it returns to SD.
    Here we test that even if data starts with noisy value, we still converge
    to stable point
    '''
    data = remove_duplicate_points(_get_test_data())[563:576]

    fixed_data = apply_filter(data, VelocityOutliersFilter(85))
    
    stationary_point = [0, 33.004964, -117.060207]
    distances = np.array([distance(stationary_point, d)
                          for d in fixed_data])

    assert(len(fixed_data) == 7)
    # filter converged after 4 steps
    assert((distances[:4] > 157000).all())
    assert((distances[4:] < 246.6).all())
    
 
def test_filter_gps():
    original_data = _get_test_data()
    assert(len(original_data) == 793)
    data = filter_gps_data(original_data)
    assert(len(data) == 782)
    assert(len(original_data)-len(data) == 11)
     
    
if __name__ == '__main__':
    test_remove_duplicate_readings()
    test_remove_outliers()
    test_remove_stationary_noise()
    test_remove_stationary_noise_return_to_stable()
    test_filter_gps()
