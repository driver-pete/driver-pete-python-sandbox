import tempfile
from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory
from driver_pete_python_sandbox.find_enpoints_procedural import find_endpoints_batch
from driver_pete_python_sandbox.filter_gps_processor import filter_gps_data
from driver_pete_python_sandbox.find_enpoints import find_endpoints


def test_find_endpoints_procedural():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_1", folder)
    
    data = filter_gps_data(read_compressed_trajectory(filename))

    endpoints_indices_batch = find_endpoints_batch(data)
    assert(len(endpoints_indices_batch) == 2)
    print(endpoints_indices_batch)
    assert(endpoints_indices_batch == [479, 670])

    endpoints = find_endpoints(data)
    assert(len(endpoints) == 2)
    assert((data[endpoints_indices_batch[0]] == endpoints[0]).all())
    assert((data[endpoints_indices_batch[1]] == endpoints[1]).all())


if __name__ == '__main__':
    test_find_endpoints_procedural()
