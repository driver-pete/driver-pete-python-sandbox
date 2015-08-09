import tempfile
from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
from driver_pete_python_sandbox.find_enpoints_procedural import find_endpoints
from driver_pete_python_sandbox.filter_gps_processor import filter_gps_data


def test_find_endpoints_procedural():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_1", folder)
    
    data = filter_gps_data(read_compressed_trajectory(filename))

    endpoints = find_endpoints(data)
    assert(len(endpoints) == 2)
    assert(endpoints == [0, 478])


if __name__ == '__main__':
    test_find_endpoints_procedural()
