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

from cogo.filter_gps import remove_duplicate_points, compute_velocities,\
    ms_to_mph, extract_delta_time, extract_delta_dist, remove_outliers
from cogo.gmaps import get_static_google_map


def _get_test_data():
    filename = os.path.join(os.path.dirname(__file__), 'test_outliers_data.pkl')
    return pickle.load(open(filename))


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

    
if __name__ == '__main__':
    test_remove_duplicate_readings()
