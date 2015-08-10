import tempfile

from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.filter_gps_processor import filter_gps_data
from driver_pete_python_sandbox.find_enpoints_procedural import find_endpoints
from driver_pete_python_sandbox.find_routes_procedural import find_routes
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory


def test_finding_paths():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_1", folder)
        
    data = filter_gps_data(read_compressed_trajectory(filename))

    endpoints = find_endpoints(data)
    assert(len(endpoints) == 2)
    assert(endpoints == [478, 669])

    AtoB_paths, BtoA_paths = find_routes(data, endpoints)
    print(AtoB_paths)
    print(BtoA_paths)
    assert(AtoB_paths == [[486, 659], [945, 1121], [1359, 1552], [2211, 2403], [2625, 2900], [3398, 3945], [4380, 4509]])
    
    # fix to start from endpoint
    #assert(BtoA_paths == [[125, 456], [679, 893], [1138, 1317], [1571, 1784], [2424, 2596], [2914, 3202], [3958, 4158]])
    assert(BtoA_paths == [[679, 893], [1138, 1317], [1571, 1784], [2424, 2596], [2914, 3202], [3958, 4158]])


if __name__ == '__main__':
    test_finding_paths()
