import tempfile
from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
from driver_pete_python_sandbox.filter_gps import filter_gps_data,\
    remove_stationary_points
from driver_pete_python_sandbox.process import find_endpoints,\
    trajectory_point_to_str, find_routes


def test_finding_paths():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_0", folder)
    
    data = filter_gps_data(read_compressed_trajectory(filename))
    # merge points which are closer than 50m 
    data = remove_stationary_points(data, distance_threshold=50)

    endpoints = find_endpoints(data)
    assert(len(endpoints) == 2)
    assert(endpoints == [0, 267])

    AtoB_paths, BtoA_paths = find_routes(data, endpoints)
    print(AtoB_paths, BtoA_paths)
    assert(AtoB_paths == [[77, 265], [438, 608], [779, 946], [1126, 1277]])
    assert(BtoA_paths == [[270, 435], [610, 775], [949, 1124], [1428, 1595]])


if __name__ == '__main__':
    test_finding_paths()