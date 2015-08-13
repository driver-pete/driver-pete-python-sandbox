from driver_pete_python_sandbox.download import S3
import os
from matplotlib.dates import date2num, num2date
import dateutil
import datetime
from pytz import timezone
from driver_pete_python_sandbox.trajectory_reader import read_compressed_trajectory,\
    write_compressed_trajectory, date_str_to_num_converter,\
    num_to_date_str_converter, date_str_to_num_converter_no_timezone


def fix_trajectory_timezone(filename, folder_to_put, change_filename=True):
    '''
    Add timezone to the trajectory
    '''
    # http://www.saltycrane.com/blog/2009/05/converting-time-zones-datetime-objects-python/
    traj = read_compressed_trajectory(filename, with_timezone=False)
    
    tz = timezone('US/Pacific')
    for i in range(traj.shape[0]):
        d = num2date(traj[i, 0])
        d = d.replace(tzinfo = None)
        d = tz.localize(d)
        traj[i, 0] = date2num(d)

    result_filename = os.path.split(filename)[-1]
    
    if change_filename:
        file_date = num2date(date_str_to_num_converter_no_timezone(result_filename))
        file_date = file_date.replace(tzinfo = None)
        file_date = tz.localize(file_date)
        result_filename = num_to_date_str_converter(date2num(file_date), with_timezone=True)
    
    resulting_path = os.path.join(folder_to_put, result_filename)
    write_compressed_trajectory(traj, os.path.join(folder_to_put, result_filename), with_timezone=True)
    return resulting_path


def fix_timezones():
    trajectories_to_fix = [
        '03-08-2015_09-58-01',
        '03-08-2015_18-34-13',
        '04-08-2015_09-24-48',
        '04-08-2015_10-42-38',
        '04-08-2015_11-36-57',
        '04-08-2015_12-42-12',
        '04-08-2015_13-22-15',
        '04-08-2015_13-50-39',
        '04-08-2015_14-36-18',
        '04-08-2015_15-46-42',
        '04-08-2015_17-30-51',
        '04-08-2015_18-28-57',
        '05-08-2015_09-45-32',
        '05-08-2015_11-27-48',
        '05-08-2015_13-41-10',
        '05-08-2015_19-40-09',
        '06-08-2015_09-50-39',
        '06-08-2015_17-42-18',
        '07-08-2015_03-48-24',
        '07-08-2015_09-49-48',
        '07-08-2015_18-36-54',
        '10-08-2015_09-47-26',
        '11-08-2015_11-06-05',
        '11-08-2015_21-11-35',
        '27-07-2015_08-46-36',
        '27-07-2015_09-19-32',
        '27-07-2015_20-21-47',
        '28-07-2015_10-03-35',
        '28-07-2015_20-09-00',
        '29-07-2015_10-16-57',
        '29-07-2015_19-16-14',
        '30-07-2015_12-53-42',
        '30-07-2015_20-38-53'] 
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
     
    for t in trajectories_to_fix:
        fix_trajectory_timezone(os.path.join(artifacts, 'raw', t),
                                os.path.join(artifacts, 'fixed'))


def fix_single_trajectory():
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    
    to_fix_path = os.path.join(artifacts, 'raw', '03-08-2015_09-58-01')
    fixed_path = fix_trajectory_timezone(to_fix_path,
                                         os.path.join(artifacts, 'fixed'))

    original_trajectory = read_compressed_trajectory(to_fix_path, with_timezone=False)
    fixed_trajectory = read_compressed_trajectory(fixed_path, with_timezone=True)
    print(num_to_date_str_converter(original_trajectory[0, 0], with_timezone=False))
    print(num_to_date_str_converter(fixed_trajectory[0, 0], with_timezone=True))


if __name__ == '__main__':
    artifacts = os.path.join(os.path.dirname(__file__), 'artifacts')
    
    to_fix_path = os.path.join(artifacts, '_testing', 'testing_raw_0')
    fixed_path = fix_trajectory_timezone(to_fix_path,
                                         os.path.join(artifacts, 'fixed'),
                                         change_filename=False)

    original_trajectory = read_compressed_trajectory(to_fix_path, with_timezone=False)
    fixed_trajectory = read_compressed_trajectory(fixed_path, with_timezone=True)
    print(num_to_date_str_converter(original_trajectory[0, 0], with_timezone=False))
    print(num_to_date_str_converter(fixed_trajectory[0, 0], with_timezone=True))
