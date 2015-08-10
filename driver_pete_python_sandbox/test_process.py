import tempfile

from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.filter_gps_processor import filter_gps_data
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
from driver_pete_python_sandbox.find_routes import find_routes
from driver_pete_python_sandbox.find_enpoints import find_endpoints


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


if __name__ == '__main__':
    test_finding_paths()
