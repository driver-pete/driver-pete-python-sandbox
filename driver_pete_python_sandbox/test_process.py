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


def test_finding_paths():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_1", folder)
        
    data = filter_gps_data(read_compressed_trajectory(filename))

    endpoints = find_endpoints(data)
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
    assert(AtoB_paths_indices == [[487, 655], [946, 1116], [1363, 1548], [2214, 2399], [2628, 2896], [4381, 4507]])
    assert(BtoA_paths_indices == [[133, 454], [682, 886], [1140, 1315], [1581, 1782], [2427, 2595], [3962, 4157]])


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
    filter_state = None
    for piece in pieces:
        vel_filter = VelocityOutliersFilter()
        if filter_state is not None:
            vel_filter.set_state(filter_state)
        filter = FilterChain([DuplicateTimeFilter(),
                              vel_filter])
        filtered_piece = apply_filter(piece, filter)
        print(piece.shape, filtered_piece.shape)
        
        #filter_state = vel_filter.get_state()
        
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
    
    assert(AtoB_paths_indices == [[487, 655], [946, 1116], [1363, 1548], [2214, 2399], [2628, 2896], [4381, 4507]])
    assert(BtoA_paths_indices == [[133, 454], [682, 886], [1140, 1315], [1581, 1782], [2427, 2595], [3962, 4157]])

if __name__ == '__main__':
    #test_finding_paths()
    test_finding_paths_with_state()
