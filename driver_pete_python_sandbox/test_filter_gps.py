# ============================================================================
# Copyright 2014 BRAIN Corporation. All rights reserved. This software is
# provided to you under BRAIN Corporation's Beta License Agreement and
# your use of the software is governed by the terms of that Beta License
# Agreement, found at http://www.braincorporation.com/betalicense.
# ============================================================================


import cPickle as pickle
import os
import numpy as np

from matplotlib.dates import datestr2num, num2date

from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
import tempfile
from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.filter_gps import compute_velocities,\
    remove_duplicate_points, ms_to_mph, remove_outliers, filter_gps_data


def _get_test_data():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_raw_0", folder)
    return read_compressed_trajectory(filename)


def test_remove_duplicate_readings():
    data = _get_test_data()
    velocities = compute_velocities(data)
    number_of_duplicates = np.sum(np.isnan(velocities))
    
    fixed_data = remove_duplicate_points(data)
    fixed_velocities = compute_velocities(fixed_data)
    assert(np.sum(np.isnan(fixed_velocities)) == 0)
    # check that we deleted duplicates only
    assert(fixed_data.shape[0] == data.shape[0] - number_of_duplicates)


def test_remove_outliers():
    data = remove_duplicate_points(_get_test_data())
    velocities = compute_velocities(data)
    outliers = np.where(velocities*ms_to_mph > 85)[0]

    fixed_data = remove_outliers(data)
    fixed_velocities = compute_velocities(fixed_data)
    fixed_outliers = np.where(fixed_velocities*ms_to_mph > 85)[0]
    assert(len(fixed_outliers) == 0)
      
    assert(fixed_data.shape[0] == data.shape[0] - len(outliers))


def test_filter_gps():
    original_data = _get_test_data()
    data = filter_gps_data(original_data)
    assert(len(original_data)-len(data) == 7)
    
    
if __name__ == '__main__':
    test_remove_duplicate_readings()
    test_remove_outliers()
    test_filter_gps()
