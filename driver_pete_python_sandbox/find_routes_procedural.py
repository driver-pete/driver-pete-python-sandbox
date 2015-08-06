
from driver_pete_python_sandbox.filter_gps import are_points_close,\
    delta_float_time
from driver_pete_python_sandbox.gmaps import trajectory_point_to_str


def find_routes(data, endpoints, verbose=False):
    assert(len(endpoints) == 2)
    current_startpoint_index = 0
    current_startpoint = endpoints[current_startpoint_index]
    current_endpoint = endpoints[current_startpoint_index-1]
    AtoB_paths = []
    BtoA_paths = []
    current_path = [current_startpoint, None]
    route_started = False
    if verbose:
        print("Staring from %s" % trajectory_point_to_str(data, current_startpoint))
    distance_to_start_route = 200
    stationary_threshold = (60*60) * 3  # hours
    for i in range(current_startpoint, len(data)):
        if not route_started:
            current_path[0] = i
            if are_points_close(data, current_startpoint, i, distance_to_start_route):
                if verbose:
                    print("Haven't gone far: %s" % trajectory_point_to_str(data, i))
            else:
                route_started = True
                if verbose:
                    print("Ok, started route: %s" % trajectory_point_to_str(data, i))
        else:
            if are_points_close(data, current_endpoint, i, distance_to_start_route):
                # route acomplished:
                current_path[1] = i
                
                if current_startpoint_index % 2 == 0:
                    AtoB_paths.append(current_path)
                    if verbose:
                        print("Route A to B from %s to %s found." % (trajectory_point_to_str(data, current_path[0]),
                                                                     trajectory_point_to_str(data, current_path[1])))
                else:
                    BtoA_paths.append(current_path)
                    if verbose:
                        print("Route B to A from %s to %s found." % (trajectory_point_to_str(data, current_path[0]),
                                                                     trajectory_point_to_str(data, current_path[1])))
                
                current_startpoint_index = (current_startpoint_index + 1) % 2
                current_startpoint = endpoints[current_startpoint_index]
                current_endpoint = endpoints[current_startpoint_index-1]
                current_path = [i, None]
                route_started = False
                if verbose:
                    print("Staring from %s" % trajectory_point_to_str(data, i))
            elif are_points_close(data, current_startpoint, i, distance_to_start_route):
                # we made a loop
                if verbose:
                    print("Made a loop from %s to %s" % (trajectory_point_to_str(data, current_path[0]),
                                                         trajectory_point_to_str(data, i)))
                current_path = [i, None]
                route_started = False
                if verbose:
                    print("Staring from %s" % trajectory_point_to_str(data, i))
            elif delta_float_time(data[i-1, 0], data[i, 0]) > stationary_threshold:
                # we made a loop
                if verbose:
                    print("Ignore stationary point %s" % (trajectory_point_to_str(data, i-1),))
                current_path = [i, None]
                route_started = False
                if verbose:
                    print("Staring from %s" % trajectory_point_to_str(data, i))
         
    return AtoB_paths, BtoA_paths
