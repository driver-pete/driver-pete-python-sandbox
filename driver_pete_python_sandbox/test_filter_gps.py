# ============================================================================
# Copyright 2014 BRAIN Corporation. All rights reserved. This software is
# provided to you under BRAIN Corporation's Beta License Agreement and
# your use of the software is governed by the terms of that Beta License
# Agreement, found at http://www.braincorporation.com/betalicense.
# ============================================================================


import numpy as np
import pprint
 
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
import tempfile
from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.filter_gps import compute_velocities,\
    remove_duplicate_points, ms_to_mph, remove_outliers, filter_gps_data,\
    extract_delta_time, extract_delta_dist
from driver_pete_python_sandbox.filter_gps_processor import apply_filter,\
    DuplicateTimeFilter, VelocityOutliersFilter
from driver_pete_python_sandbox.gmaps import trajectory_point_to_str
 
 
def _get_test_data():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_raw_0", folder)
    data = read_compressed_trajectory(filename)
    # add few duplicates
    data[54] = data[53]
    data[100] = data[99]
    return data
 
 
def test_remove_duplicate_readings():
    data = _get_test_data()
    velocities = compute_velocities(data)
    number_of_duplicates = np.sum(np.isnan(velocities))
     
    fixed_data = remove_duplicate_points(data)
    fixed_velocities = compute_velocities(fixed_data)
    assert(np.sum(np.isnan(fixed_velocities)) == 0)
    # check that we deleted duplicates only
    assert(fixed_data.shape[0] == data.shape[0] - number_of_duplicates)
    
    fixed_data_processor = apply_filter(data, DuplicateTimeFilter())
    assert((fixed_data == fixed_data_processor).all())
    
 
def test_remove_outliers():
    np.set_printoptions(suppress=True)
    data = remove_duplicate_points(_get_test_data())[561:576]
    
    velocities = compute_velocities(data)
    outliers = np.where(velocities*ms_to_mph > 85)[0]
 
    fixed_data = remove_outliers(data)
    fixed_velocities = compute_velocities(fixed_data)
    fixed_outliers = np.where(fixed_velocities*ms_to_mph > 85)[0]
    assert(len(fixed_outliers) == 0)
       
    #assert(fixed_data.shape[0] == data.shape[0] - len(outliers))
    
    delta_time = extract_delta_time(data)
    delta_dist = extract_delta_dist(data)
    print('------ORIGINAL--------')
    for i in range(data.shape[0]-1):
        print("%s: ds: %s, v: %s" % (trajectory_point_to_str(data, i), delta_dist[i], velocities[i]*ms_to_mph))

    print('Outliers:')
    print(outliers)
   
#     print('-----BATCH--------')
#     for d in fixed_data:
#         print(trajectory_point_to_str([d], 0)) 
    
    
    print('-----PROCESSOR--------')
    fixed_data_processor = apply_filter(data, VelocityOutliersFilter(85))
    for d in fixed_data_processor:
        print(trajectory_point_to_str([d], 0)) 

    
#     for d in fixed_data:
#         print(trajectory_point_to_str([d], 0))
    #assert(fixed_data_processor.shape[0] == data.shape[0] - len(outliers))
 
 
def test_filter_gps():
    original_data = _get_test_data()
    data = filter_gps_data(original_data)
    assert(len(original_data)-len(data) == 9)
     
    
if __name__ == '__main__':
    #test_remove_duplicate_readings()
    test_remove_outliers()
    #test_filter_gps()
