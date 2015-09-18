import tempfile

from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.filter_gps_processor import filter_gps_data,\
    FilterChain, DuplicateTimeFilter,\
    VelocityOutliersFilter, apply_filter
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
from driver_pete_python_sandbox.find_routes import find_routes, RoutesFinder
from driver_pete_python_sandbox.find_enpoints import find_endpoints,\
    FindEndpoints
import numpy as np
from driver_pete_python_sandbox.gmaps import trajectory_point_to_str
from driver_pete_python_sandbox.process import Path


def _extract_indices(data, paths):
    result = []
    for p in paths:
        indices = [(data[:, 0] == p[0, 0]).nonzero()[0][0],
                   (data[:, 0] == p[p.shape[0]-1, 0]).nonzero()[0][0]]
        result.append(indices)
    return result


def _get_point_index(data, point):
    return (data[:, 0] == point[0]).nonzero()[0][0]


def test_finding_paths():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_1", folder)
        
    data = filter_gps_data(read_compressed_trajectory(filename))
    
    endpoints = find_endpoints(data)
    assert(len(endpoints) == 2)
    print(trajectory_point_to_str(data, _get_point_index(data, endpoints[0])))
    print(trajectory_point_to_str(data, _get_point_index(data, endpoints[1])))
    assert(_get_point_index(data, endpoints[0]) == 479)
    assert(_get_point_index(data, endpoints[1]) == 670)

    AtoB_paths, BtoA_paths = find_routes(data, endpoints, verbose=False)

    AtoB_paths_indices = _extract_indices(data, AtoB_paths)
    BtoA_paths_indices = _extract_indices(data, BtoA_paths)
    print(AtoB_paths_indices)
    print(BtoA_paths_indices)
    assert(AtoB_paths_indices == [[488, 656], [947, 1117], [1364, 1549], [2216, 2401], [2630, 2898], [4400, 4526]])
    assert(BtoA_paths_indices == [[134, 455], [683, 887], [1141, 1316], [1582, 1783], [2429, 2597], [3975, 4170]])


def test_finding_paths_with_state():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_1", folder)
    full_trajectory = read_compressed_trajectory(filename)
    
    pieces = []
    pieces.append(full_trajectory[0:480])
    pieces.append(full_trajectory[480:2000])
    pieces.append(full_trajectory[2000:3000])
    pieces.append(full_trajectory[3000:4000])
    pieces.append(full_trajectory[4000:])
    
    filtered_pieces = []
    endpoints = []
    
    findendpoints_state = None
    filter_state = None
    for piece in pieces:
        vel_filter = VelocityOutliersFilter()
        if filter_state is not None:
            vel_filter.set_state(filter_state)
        filter = FilterChain([DuplicateTimeFilter(),
                              vel_filter])
        filtered_piece = apply_filter(piece, filter)
        
        filter_state = vel_filter.get_state()
        
        filtered_pieces.append(filtered_piece)
        
        finder = FindEndpoints(endpoints=endpoints)
        if findendpoints_state is not None:
            finder.set_state(findendpoints_state)
        for d in filtered_piece:
            finder.process(d)
        endpoints = finder.get_endpoints()
        findendpoints_state = finder.get_state()

    data = np.vstack(filtered_pieces)
    assert(_get_point_index(data, endpoints[0]) == 479)
    assert(_get_point_index(data, endpoints[1]) == 670)

    AtoB_paths = []
    BtoA_paths = []
    
    finder_current_route = []
    finder_endpoint_index = None
    for piece in filtered_pieces:
        
        finder = RoutesFinder(endpoints)
        finder.set_state(finder_current_route, finder_endpoint_index)
        
        for d in piece:
            finder.process(d)

        finder_current_route, finder_endpoint_index = finder.get_state()
        
        AtoB_paths_piece, BtoA_paths_piece = finder.get_routes()
        AtoB_paths += AtoB_paths_piece
        BtoA_paths += BtoA_paths_piece

    AtoB_paths_indices = _extract_indices(data, AtoB_paths)
    BtoA_paths_indices = _extract_indices(data, BtoA_paths)
    print(AtoB_paths_indices)
    print(BtoA_paths_indices)
    
    assert(AtoB_paths_indices == [[488, 656], [947, 1117], [1364, 1549], [2216, 2401], [2630, 2898], [4400, 4526]])
    assert(BtoA_paths_indices == [[134, 455], [683, 887], [1141, 1316], [1582, 1783], [2429, 2597], [3975, 4170]])


def test_finding_paths_with_state_2():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    pieces = []
    pieces_keys = [
        "_testing/testing_sequence0/data/14-09-2015_09-15-01_PDT",
        "_testing/testing_sequence0/data/14-09-2015_11-03-24_PDT",
        "_testing/testing_sequence0/data/14-09-2015_13-49-55_PDT",
        "_testing/testing_sequence0/data/14-09-2015_18-20-13_PDT",
        "_testing/testing_sequence0/data/14-09-2015_19-59-23_PDT",
        "_testing/testing_sequence0/data/15-09-2015_09-32-15_PDT",
        "_testing/testing_sequence0/data/15-09-2015_22-31-21_PDT"
    ]
    for k in pieces_keys:
        filename = s3.download(k, folder)
        pieces.append(read_compressed_trajectory(filename))
        
    filtered_pieces = []
    endpoints = []
    
    findendpoints_state = None
    filter_state = None
    for pi, piece in enumerate(pieces):
        vel_filter = VelocityOutliersFilter()
        if filter_state is not None:
            vel_filter.set_state(filter_state)
        filter = FilterChain([DuplicateTimeFilter(),
                              vel_filter])
        filtered_piece = apply_filter(piece, filter)

        filter_state = vel_filter.get_state()
        
        filtered_pieces.append(filtered_piece)
        
        finder = FindEndpoints(endpoints=endpoints)
        if findendpoints_state is not None:
            finder.set_state(findendpoints_state)
        for i, d in enumerate(filtered_piece):
            finder.process(d)
        endpoints = finder.get_endpoints()
        findendpoints_state = finder.get_state()

    data = np.vstack(filtered_pieces)
    
    print(trajectory_point_to_str(data, _get_point_index(data, endpoints[0])))
    print(trajectory_point_to_str(data, _get_point_index(data, endpoints[1])))

    assert(len(endpoints) == 2)
    assert(_get_point_index(data, endpoints[0]) == 5)
    assert(_get_point_index(data, endpoints[1]) == 122)

    AtoB_paths = []
    BtoA_paths = []
    
    finder_current_route = []
    finder_endpoint_index = None
    for piece in filtered_pieces:
        
        finder = RoutesFinder(endpoints)
        finder.set_state(finder_current_route, finder_endpoint_index)
        
        for d in piece:
            finder.process(d)

        finder_current_route, finder_endpoint_index = finder.get_state()
        
        AtoB_paths_piece, BtoA_paths_piece = finder.get_routes()
        AtoB_paths += AtoB_paths_piece
        BtoA_paths += BtoA_paths_piece

    AtoB_paths_indices = _extract_indices(data, AtoB_paths)
    BtoA_paths_indices = _extract_indices(data, BtoA_paths)
    
    print(AtoB_paths_indices)
    print(BtoA_paths_indices)
    assert(AtoB_paths_indices == [[11, 111], [556, 730]])
    assert(BtoA_paths_indices == [[288, 387]])


if __name__ == '__main__':
    test_finding_paths()
    test_finding_paths_with_state()
    test_finding_paths_with_state_2()
