import os

from expts.analysis.summarise import prune, summarise
from expts.bouts.bouts import extract_bouts, process_bouts
from expts.trajectory.trajectories import extract_trajectories
from expts.utils.combine import combine_multi


def pipeline(data_folder, tracked_f, bouts_ts_f, session_f, group_f, trial_duration):
    traj_ts_f = 'traj_ts.feather'
    extract_trajectories(data_folder, tracked_fname=tracked_f, traj_ts_f=traj_ts_f, trial_duration=trial_duration)
    extract_bouts(data_folder, traj_ts_f=traj_ts_f, bouts_ts_f=bouts_ts_f)
    summarise(data_folder, bouts_ts_f=bouts_ts_f, session_f=session_f, group_f=group_f)


def or_pipeline(folder, tracked_f, bouts_ts_f, session_f, group_f):
    # def trial_duration(stimulus_speed):
    #     """Return trial duration in seconds given stimulus speed in mm/s
    #     """
    #     durations = {2: 150, 4: 75, 6: 50, 8: 37.5, 10: 30}
    #     return durations[stimulus_speed]

    def trial_duration(*_args):
        """Return trial duration in seconds"""
        return 60

    pipeline(folder, tracked_f=tracked_f, bouts_ts_f=bouts_ts_f, session_f=session_f, group_f=group_f,
             trial_duration=trial_duration)


def bf_pipeline(folder, tracked_f, bouts_ts_f, session_f, group_f):
    def trial_duration(*_args):
        """Return trial duration in seconds"""
        return 60

    pipeline(folder, tracked_f=tracked_f, bouts_ts_f=bouts_ts_f, session_f=session_f, group_f=group_f,
             trial_duration=trial_duration)


def process_expt_data():
    """
    Process experimental data for both OR and BF procedures
    """
    # base_folder = '~/data/ezfish/analysis'  # base folder
    base_folder = '../data/expt'  # base folder
    bf_subfolder = 'bf'  # subfolder for BF procedure
    or_subfolder = 'or'  # subfolder for OR procedure
    all_subfolder = 'all'  # subfolder for combined data from both procedures
    # tracked_f = 'tracked.feather'  # filename for input data of tracked positions
    tracked_f = 'tracked.csv.gz'  # filename for input data of tracked positions
    bouts_ts_f = 'bouts_ts.feather'  # filename for timeseries data including trajectory and bout info
    bouts_f = 'bouts.feather'  # filename for output bout-level data
    session_f = 'session.csv'  # filename for session-level summary
    group_f = 'group_summ.csv'  # filename for group summary
    group_pruned_f = 'group_summ_pruned.csv'  # filename for group summary data excluding outliers

    base_folder = os.path.abspath(os.path.expanduser(base_folder))
    or_folder = os.path.join(base_folder, or_subfolder)
    bf_folder = os.path.join(base_folder, bf_subfolder)
    all_folder = os.path.join(base_folder, all_subfolder)
    print('Processing OR data')
    or_pipeline(or_folder, tracked_f=tracked_f, bouts_ts_f=bouts_ts_f, session_f=session_f, group_f=group_f)
    print('Processing BF data')
    bf_pipeline(bf_folder, tracked_f=tracked_f, bouts_ts_f=bouts_ts_f, session_f=session_f, group_f=group_f)
    print('Removing outliers from group summaries')
    prune(group_f, [or_folder, bf_folder], group_pruned_f)
    print('Combining timeseries data and group summaries for both experiments')
    combine_multi([bouts_ts_f, group_f, group_pruned_f], [or_folder, bf_folder], ['OR', 'BF'], all_folder)
    process_bouts(datadir=all_folder, bouts_ts_f=bouts_ts_f, bouts_f=bouts_f)


if __name__ == '__main__':
    process_expt_data()
