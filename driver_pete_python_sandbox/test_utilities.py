# ============================================================================
# Copyright 2014 BRAIN Corporation. All rights reserved. This software is
# provided to you under BRAIN Corporation's Beta License Agreement and
# your use of the software is governed by the terms of that Beta License
# Agreement, found at http://www.braincorporation.com/betalicense.
# ============================================================================
from driver_pete_python_sandbox.trajectory_reader import date_str_to_num_converter
from driver_pete_python_sandbox.utilities import delta_float_time, distance


def test_delta_time():
    datestr_array = [
        '04-08-2015_14-35-50_PDT',
        '04-08-2015_14-52-31_PDT',
        '04-08-2015_14-52-37_PDT',
        '04-08-2015_14-59-30_PDT',
        '04-08-2015_14-59-30_PDT',
        '05-08-2015_15-46-30_PDT',
        '05-09-2015_15-46-38_PDT',
    ]
    
    dates_nums = [date_str_to_num_converter(el) for el in datestr_array]
    
    dts = []
    for i in range(len(dates_nums) - 1):
        dts.append(delta_float_time(dates_nums[i], dates_nums[i+1]))

    expected_dts = [1001, 6, 413, 0, 89220, 2678408]
    assert(expected_dts == dts)


def test_delta_dist():
    data_points = [
        [0, 32.936004, -117.23537],
        [0, 32.934912, -117.236338],
        [0, 32.935667, -117.235796],
        [0, 32.935667, -117.235796],
        [0, 32.936034, -117.23537],
    ]
    
    ds = []
    for i in range(len(data_points) - 1):
        ds.append(distance(data_points[i], data_points[i+1]))

    expected_ds = [151.20243391843636, 97.87941457631524, 0.0, 56.95460850285275]
    assert(expected_ds == ds)


if __name__ == '__main__':
    test_delta_time()
    test_delta_dist()
