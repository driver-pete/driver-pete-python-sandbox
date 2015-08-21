
from driver_pete_python_sandbox.filter_gps import delta_float_time
from driver_pete_python_sandbox.utilities import distance


class FindEndpoints(object):
    def __init__(self, stationary_threshold = (60*60)*3, endpoints_distance = 1000., endpoints=[]):
        self._stationary_threshold = stationary_threshold
        self._endpoints_distance = endpoints_distance
        self._endpoints = endpoints
        self._prev_point = None
    
    def process(self, point):
        if self._prev_point is None:
            self._prev_point = point
            return
        
        dt = delta_float_time(self._prev_point[0], point[0])
        if dt > self._stationary_threshold:
            if not self._endpoint_exists(self._prev_point):
                self._endpoints.append(self._prev_point)
        self._prev_point = point

    def get_endpoints(self):
        return self._endpoints

    def _endpoint_exists(self, endpoint):
        for e in self._endpoints:
            if distance(endpoint, e) < self._endpoints_distance:
                return True
        return False

    def set_prev_point(self, prev_point):
        self._prev_point = prev_point
        
    def get_prev_point(self):
        return self._prev_point
            

def find_endpoints(data):
    finder = FindEndpoints()
    for d in data:
        finder.process(d)
    return finder.get_endpoints()
