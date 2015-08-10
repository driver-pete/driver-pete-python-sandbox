from driver_pete_python_sandbox.filter_gps import extract_delta_time,\
    are_points_close
import numpy as np


def find_endpoints_batch(data):
    # get delta time array in seconds
    delta_time = extract_delta_time(data) 

    # get indices on the trajectory where we spend a lot of time still
    stationary_threshold = (60*60) * 3  # hours
    stationary_points = np.where(delta_time>stationary_threshold)[0]
    #stationary_points = [0] + list(stationary_points) + [data.shape[0]-1]
    
    # filter out stationary points that are driving-distance (1km) close to each other
    is_index_close = lambda index1, index2: are_points_close(data, index1, index2, 1000)

    unique_locations = [stationary_points[0]]
    for s in stationary_points:
        candidates = [u for u in unique_locations
                      if is_index_close(s, u)]
        # location is unique if no candidates found
        if len(candidates) == 0:
            unique_locations.append(s)

    return unique_locations
