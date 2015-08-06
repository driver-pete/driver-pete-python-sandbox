import tempfile
from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
from driver_pete_python_sandbox.filter_gps import filter_gps_data,\
    remove_stationary_points
from driver_pete_python_sandbox.find_enpoints_procedural import find_endpoints


def test_find_endpoints_procedural():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_0", folder)
    
    data = filter_gps_data(read_compressed_trajectory(filename))
    # merge points which are closer than 50m 
    data = remove_stationary_points(data, distance_threshold=50)

    endpoints = find_endpoints(data)
    assert(len(endpoints) == 2)
    assert(endpoints == [0, 267])


if __name__ == '__main__':
    test_find_endpoints_procedural()