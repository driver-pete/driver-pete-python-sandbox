import os
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory,\
    write_compressed_trajectory
import numpy as np


def merge_trajectories(raw_trajectories_folder, results_file):
    onlyfiles = [f for f in os.listdir(raw_trajectories_folder)
                 if os.path.isfile(os.path.join(raw_trajectories_folder, f)) ]
    
    contents = []
    for name in onlyfiles:
        full_name = os.path.join(raw_trajectories_folder, name)
        contents.append(read_compressed_trajectory(full_name))
     
    contents.sort(key=lambda p: p[0, 0], reverse=False)   

    merged_traj = np.vstack(contents)
    write_compressed_trajectory(merged_traj, results_file)
    

if __name__ == '__main__':
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    merge_trajectories(os.path.join(artifacts, 'raw'),
                       os.path.join(artifacts, 'merged'))
