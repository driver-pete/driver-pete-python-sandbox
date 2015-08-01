from driver_pete_python_sandbox.download import S3
import os
from matplotlib.dates import date2num, num2date
import dateutil
import datetime
from pytz import timezone
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory



def fix_trajectory(filename, folder_to_put):
    # http://www.saltycrane.com/blog/2009/05/converting-time-zones-datetime-objects-python/
    traj = read_compressed_trajectory(filename)
    delta = datetime.timedelta(hours=12)
    
    for i in range(traj.shape[0]):
        d = num2date(traj[i, 0])
        traj[i, 0] = date2num(d + delta)
        d2 = num2date(traj[i, 0])
        print(str(d), str(d2))



if __name__ == '__main__':
    trajectories_to_fix = ['27-7-2015_08-21-47',
                           '28-7-2015_08-09-00',
                           '29-7-2015_07-16-14',
                           '30-7-2015_08-38-53']
    
    traj = trajectories_to_fix[0]
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    
    
    fix_trajectory(os.path.join(artifacts, 'raw', trajectories_to_fix[0]),
                    os.path.join(artifacts, 'fixed'))