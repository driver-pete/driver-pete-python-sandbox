
from driver_pete_python_sandbox.filter_gps import delta_float_time
from driver_pete_python_sandbox.utilities import distance
from driver_pete_python_sandbox.gmaps import trajectory_point_to_str


class FindEndpoints(object):
    def __init__(self, stationary_threshold = (60*60)*5, endpoints_distance = 1000., endpoints=[],
                 stationary_distance_threshold = 500):
        self._stationary_threshold = stationary_threshold
        assert(stationary_distance_threshold < endpoints_distance)
        self._endpoints_distance = endpoints_distance
        self._stationary_distance_threshold = stationary_distance_threshold
        self._endpoints = endpoints
        self._prev_point = None
        self._hypothesis_point = None
        self._current_cumulative_dt = 0
    
    def process(self, point):
        if self._prev_point is None:
            self._prev_point = point
            return
        
        # if there is no hypothesis, lets see if we far away from the existing endpoint
        if self._hypothesis_point is None:
            if not self._endpoint_exists(self._prev_point):
                self._hypothesis_point = self._prev_point
            else:
                self._prev_point = point
                return
        
        ds = distance(self._hypothesis_point, self._prev_point)
        if ds < self._stationary_distance_threshold:
            dt = delta_float_time(self._prev_point[0], point[0])
            # if we time contribution is large, then shift hypothesis point to the most recent onec
            if dt > self._current_cumulative_dt:
                self._hypothesis_point = self._prev_point
            self._current_cumulative_dt += dt
            if self._current_cumulative_dt > self._stationary_threshold:
                self._endpoints.append(self._hypothesis_point)
                self._hypothesis_point = None
                self._current_cumulative_dt = 0
        else:
            # moved too far from hypothesis point, reseting
            self._hypothesis_point = None
            self._current_cumulative_dt = 0
        self._prev_point = point

    def get_endpoints(self):
        return self._endpoints

    def _endpoint_exists(self, endpoint):
        for e in self._endpoints:
            if distance(endpoint, e) < self._endpoints_distance:
                return True
        return False

    def set_state(self, state):
        self._prev_point, self._hypothesis_point, self._current_cumulative_dt = state
        
    def get_state(self):
        return self._prev_point, self._hypothesis_point, self._current_cumulative_dt


def find_endpoints(data):
    finder = FindEndpoints()
    for i, d in enumerate(data):
        #print(' - %s' % trajectory_point_to_str(data, i))
        finder.process(d)
    return finder.get_endpoints()
