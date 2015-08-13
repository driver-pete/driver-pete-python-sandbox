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


def distance(datapoint1, datapoint2):
    return vincenty(datapoint1[1:], datapoint2[1:]).meters
