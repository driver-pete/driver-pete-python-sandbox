import os
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory,\
    write_compressed_trajectory
import numpy as np
from driver_pete_python_sandbox.filter_gps import extract_delta_time
from driver_pete_python_sandbox.filter_gps_processor import apply_filter,\
    DuplicateTimeFilter


def merge_trajectories(raw_trajectories_folder, results_file):
    onlyfiles = [f for f in os.listdir(raw_trajectories_folder)
                 if os.path.isfile(os.path.join(raw_trajectories_folder, f))]
    
    contents = []
    for name in onlyfiles:
        full_name = os.path.join(raw_trajectories_folder, name)
        contents.append(read_compressed_trajectory(full_name))
     
    contents.sort(key=lambda p: p[0, 0], reverse=False)    
    merged_traj = np.vstack(contents)
    merged_traj = apply_filter(merged_traj, DuplicateTimeFilter())
    dt = extract_delta_time(merged_traj)
    assert((dt > 0).all())
    write_compressed_trajectory(merged_traj, results_file)
    

if __name__ == '__main__':
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    merge_trajectories(os.path.join(artifacts, 'raw'),
                       os.path.join(artifacts, 'merged'))
