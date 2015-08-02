from driver_pete_python_sandbox.download import S3
import os
from matplotlib.dates import date2num, num2date
import dateutil
import datetime
from pytz import timezone
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory,\
    write_compressed_trajectory, date_str_to_num_converter,\
    num_to_date_str_converter


def fix_trajectory(filename, folder_to_put):
    '''
    This function shifts the time 12 hours forward for the trajectory.
    This was necessary to fix trajectory with am/pm format to 24 hours format of date str.
    '''
    # http://www.saltycrane.com/blog/2009/05/converting-time-zones-datetime-objects-python/
    traj = read_compressed_trajectory(filename)
    delta = datetime.timedelta(hours=12)
    
    for i in range(traj.shape[0]):
        d = num2date(traj[i, 0])
        traj[i, 0] = date2num(d + delta)

    result_filename = os.path.split(filename)[-1]
    file_date = num2date(date_str_to_num_converter(result_filename))
    file_date = file_date + delta
    result_filename = num_to_date_str_converter(date2num(file_date))
    write_compressed_trajectory(traj, os.path.join(folder_to_put, result_filename))


def fix_am_pm():
    trajectories_to_fix = ['27-7-2015_08-21-47',
                           '28-7-2015_08-09-00',
                           '29-7-2015_07-16-14',
                           '30-7-2015_08-38-53']
    
    traj = trajectories_to_fix[0]
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    
    for t in trajectories_to_fix:
        fix_trajectory(os.path.join(artifacts, 'raw', t),
                       os.path.join(artifacts, 'fixed'))



if __name__ == '__main__':
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    traj = read_compressed_trajectory(os.path.join(artifacts, 'raw', '30-07-2015_20-38-53'))
    for t in traj:
        d = num2date(t[0])
        if d.hour == 0:
            t[0] = date2num(d - datetime.timedelta(hours=12))
    
    write_compressed_trajectory(traj, os.path.join(artifacts, 'fixed', '30-07-2015_20-38-53'))
