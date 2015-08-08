
import os
import tempfile
from driver_pete_python_sandbox.download import S3
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory,\
    write_compressed_trajectory


def test_trajectory_reader():
    folder = tempfile.mkdtemp()
    s3 = S3('driverpete-storage')
    filename = s3.download("_testing/testing_merged_0", folder)
    trajectory = read_compressed_trajectory(filename)
    write_compressed_trajectory(trajectory, os.path.join(folder, 'trajectory_copy'))
    trajectory_copy = read_compressed_trajectory(os.path.join(folder, 'trajectory_copy'))
    assert((trajectory == trajectory_copy).all())
