from driver_pete_python_sandbox.filter_gps import extract_delta_time
import numpy as np
from driver_pete_python_sandbox.utilities import distance


def find_endpoints_batch(data):
    # get delta time array in seconds
    delta_time = extract_delta_time(data) 

    # get indices on the trajectory where we spend a lot of time still
    stationary_threshold = (60*60) * 3  # hours
    stationary_points = np.where(delta_time>stationary_threshold)[0]
    
    # filter out stationary points that are driving-distance (1km) close to each other
    is_index_close = lambda index1, index2: distance(data[index1], data[index2]) < 1000

    unique_locations = [stationary_points[0]]
    for s in stationary_points:
        candidates = [u for u in unique_locations
                      if is_index_close(s, u)]
        # location is unique if no candidates found
        if len(candidates) == 0:
            unique_locations.append(s)

    return unique_locations
