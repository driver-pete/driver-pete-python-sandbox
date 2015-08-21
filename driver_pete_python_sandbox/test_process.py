import tempfile

from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.filter_gps_processor import filter_gps_data,\
    FilterChain, DuplicateTimeFilter, StationaryPointsFilter,\
    VelocityOutliersFilter, apply_filter
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
from driver_pete_python_sandbox.find_routes import find_routes, RoutesFinder
from driver_pete_python_sandbox.find_enpoints import find_endpoints,\
    FindEndpoints
import numpy as np


def test_finding_paths():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_1", folder)
        
    data = filter_gps_data(read_compressed_trajectory(filename))

    endpoints = find_endpoints(data)
    assert(len(endpoints) == 2)
    assert((data[:, 0] == endpoints[0][0]).nonzero()[0][0] == 478)
    assert((data[:, 0] == endpoints[1][0]).nonzero()[0][0] == 669)

    AtoB_paths, BtoA_paths = find_routes(data, endpoints, verbose=False)
    
    def _extract_indices(data, paths):
        result = []
        for p in paths:
            indices = [(data[:, 0] == p[0, 0]).nonzero()[0][0],
                       (data[:, 0] == p[p.shape[0]-1, 0]).nonzero()[0][0]]
            result.append(indices)
        return result

    AtoB_paths_indices = _extract_indices(data, AtoB_paths)
    BtoA_paths_indices = _extract_indices(data, BtoA_paths)
    print(AtoB_paths_indices)
    print(BtoA_paths_indices)
    assert(AtoB_paths_indices == [[485, 659], [944, 1121], [1358, 1552], [2210, 2403], [2624, 2900], [4379, 4509]])
    assert(BtoA_paths_indices == [[124, 456], [678, 893], [1137, 1317], [1570, 1784], [2423, 2596], [3957, 4158]])


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
    
    findendpoints_prev_point = None
    for piece in pieces:
        vel_filter = VelocityOutliersFilter(speed_mph_thershold=85.)
        filter = FilterChain([DuplicateTimeFilter(),
                              StationaryPointsFilter(1.),
                              vel_filter])
        filtered_piece = apply_filter(piece, filter)
        filtered_pieces.append(filtered_piece)
        
        finder = FindEndpoints(endpoints=endpoints)
        finder.set_prev_point(findendpoints_prev_point)
        i = 0
        for d in filtered_piece:
            finder.process(d)
        endpoints = finder.get_endpoints()
        findendpoints_prev_point = finder.get_prev_point()

    data = np.vstack(filtered_pieces)
    assert((data[:, 0] == endpoints[0][0]).nonzero()[0][0] == 478)
    assert((data[:, 0] == endpoints[1][0]).nonzero()[0][0] == 669)

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

    def _extract_indices(data, paths):
        result = []
        for p in paths:
            indices = [(data[:, 0] == p[0, 0]).nonzero()[0][0],
                       (data[:, 0] == p[p.shape[0]-1, 0]).nonzero()[0][0]]
            result.append(indices)
        return result

    AtoB_paths_indices = _extract_indices(data, AtoB_paths)
    BtoA_paths_indices = _extract_indices(data, BtoA_paths)
    print(AtoB_paths_indices)
    print(BtoA_paths_indices)
    assert(AtoB_paths_indices == [[485, 659], [944, 1121], [1358, 1552], [2210, 2403], [2624, 2900], [4379, 4509]])
    assert(BtoA_paths_indices == [[124, 456], [678, 893], [1137, 1317], [1570, 1784], [2423, 2596], [3957, 4158]])

if __name__ == '__main__':
    test_finding_paths_with_state()
