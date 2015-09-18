
from driver_pete_python_sandbox.filter_gps import delta_float_time
from driver_pete_python_sandbox.gmaps import trajectory_point_to_str
import numpy as np
from driver_pete_python_sandbox.utilities import distance


class RoutesFinder(object):
    def __init__(self, endpoints, distance_to_start_route=400, continuity_threshold=60*10, verbose=False):
        self._endpoints = endpoints
        assert(len(self._endpoints) == 2)
        self._distance_to_start_route = distance_to_start_route
        self._continuity_threshold = continuity_threshold
        self._AtoB_routes = []
        self._BtoA_routes = []
        self._current_route = []
        self._from_endpoint_index = None
        self._verbose = verbose

    def _start_route(self, point, endpoint_index):
        assert(endpoint_index is not None)
        self._from_endpoint_index = endpoint_index
        self._current_route.append(point)
        if self._verbose:
            print('Starting route from %s' % trajectory_point_to_str([point], 0))

    def _to_endpoint_index(self):
        return (self._from_endpoint_index + 1) % 2

    def _stop_route(self):
        self._current_route = []
        self._from_endpoint_index = None
        if self._verbose:
            print('stopping route')

    def _get_closest_endpoint_index(self, point):
        for i in range(len(self._endpoints)):
            if distance(point, self._endpoints[i]) < self._distance_to_start_route:
                return i
        return None

    def process(self, point):
        if self._from_endpoint_index is None:
            index = self._get_closest_endpoint_index(point)
            if index is not None:
                self._start_route(point, index)
            return
        else:
            dt = delta_float_time(self._current_route[-1][0], point[0])
            if dt > self._continuity_threshold:
                if self._verbose:
                    dist = distance(point, self._endpoints[self._from_endpoint_index])
                    print('Continuity ruined from %s\n    to %s\n   dt=%smin, dist=%s' %
                          (trajectory_point_to_str([self._current_route[-1]], 0),
                           trajectory_point_to_str([point], 0),
                           dt/60., dist))
                index = self._get_closest_endpoint_index(point)
                if index == self._from_endpoint_index:
                    if self._verbose:
                        print(' !BUT Didnt move too far from beginning though')
                    self._stop_route()
                    self._start_route(point, index)
                else:
                    self._stop_route()
                return
            
            self._current_route.append(point)

            index = self._get_closest_endpoint_index(point)
            if index == self._from_endpoint_index:
                if self._verbose:
                    print('made a loop or didnt move')
                self._stop_route()
                self._start_route(point, index)
            elif index == self._to_endpoint_index():
                if self._from_endpoint_index == 0:
                    self._AtoB_routes.append(np.array(self._current_route))
                    if self._verbose:
                        print('A to B found: %s TO %s' %
                              (trajectory_point_to_str(self._current_route, 0),
                               trajectory_point_to_str(self._current_route, len(self._current_route)-1)))
                    self._stop_route()
                    
                else:
                    self._BtoA_routes.append(np.array(self._current_route))
                    if self._verbose:
                        print('B to A found: %s TO %s' %
                              (trajectory_point_to_str(self._current_route, 0),
                               trajectory_point_to_str(self._current_route, len(self._current_route)-1)))
                    self._stop_route()

    def get_routes(self):
        return self._AtoB_routes, self._BtoA_routes

    def set_state(self, current_route, from_endpoint_index):
        self._current_route = current_route
        self._from_endpoint_index = from_endpoint_index

    def get_state(self):
        return self._current_route, self._from_endpoint_index


def find_routes(data, endpoints, verbose=False):
    finder = RoutesFinder(endpoints, verbose=verbose)
    for i, d in enumerate(data):
        if verbose:
            print("   - %s" % trajectory_point_to_str(data, i))
        finder.process(d)
         
    return finder.get_routes()
