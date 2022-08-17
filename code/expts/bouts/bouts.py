"""Combine data from OMR regulation and baseline flow experiments"""
import os

from expts.analysis.bout_summ import summarise_bouts, bouts_data
from expts.bouts.add_bout_data import add_bout_data
from expts.bouts.identify_bouts import identify_bouts
from expts.bouts.profile import calc_profiles
from expts.utils.persist import load_data, save_data


def extract_bouts(datadir, traj_ts_f, bouts_ts_f):
    """
    Add bout data to trajectory timeseries data
    :param datadir: data folder name
    :param traj_ts_f: filename for input trajectory timeseries data
    :param bouts_ts_f: filename for output timeseries including bout data
    :return:
    """
    inpath = os.path.join(datadir, traj_ts_f)
    bout_ids_f = 'bout_ids.feather'
    bout_ids_path = os.path.join(datadir, bout_ids_f)
    bouts_ts_path = os.path.join(datadir, bouts_ts_f)
    identify_bouts(inpath=inpath, outpath=bout_ids_path)
    add_bout_data(infile=bout_ids_path, outfile=bouts_ts_path)


# def bouts_datafile(inpath, outpath):
#     df = load_data(inpath)
#     df = df[df.bout_num != -1]  # include only valid bouts
#
#     idx_cols = ['id', 'height', 'stimulus_speed', 'direction', 'seg_id', 'bout_num']
#     # idx_cols = ['source', 'id', 'height', 'stimulus_speed', 'direction', 'seg_id', 'bout_num']
#     bout_cols = ['bout_initial_speed', 'bout_peak_speed', 'bout_displacement', 'bout_duration',
#                  'omr_bout', 'active_duration']
#
#     bouts_df = df[idx_cols + bout_cols].groupby(idx_cols).first().reset_index()
#     print(f'total bouts: {len(bouts_df)}')
#
#     save_data(bouts_df, outpath)


def process_bouts(datadir, bouts_ts_f, bouts_f, bouts_sess_summ_f, bouts_group_summ_f):
    """
    Compute and save intensity profiles and bout-level data from timeseries bout data

    :param datadir: folder containing combined data
    :param bouts_ts_f: filename for input bout timeseries data
    :param bouts_f: filename for output bout level data
    """
    # generate bout profile data
    bouts_ts_path = os.path.join(datadir, bouts_ts_f)
    all_profile_path = os.path.join(datadir, 'all_profile.csv')
    omr_profile_path = os.path.join(datadir, 'omr_profile.csv')
    calc_profiles(infile=bouts_ts_path, omrfile=omr_profile_path, allfile=all_profile_path)

    # generate bout-level data summaries
    bouts_path = os.path.join(datadir, bouts_f)
    bouts_sess_summ_path=os.path.join(datadir, bouts_sess_summ_f)
    bouts_group_summ_path=os.path.join(datadir, bouts_group_summ_f)
    bouts_data(bouts_ts_path, bouts_path)
    summarise_bouts(bouts_path, bouts_sess_summ_path, bouts_group_summ_path)

# def process_bouts(datadir, bouts_ts_f, bouts_f):
#     """
#     Compute and save intensity profiles and bout-level data from timeseries bout data
#
#     :param datadir: folder containing combined data
#     :param bouts_ts_f: filename for input bout timeseries data
#     :param bouts_f: filename for output bout level data
#     """
#     # generate bout profile data
#     bouts_ts_path = os.path.join(datadir, bouts_ts_f)
#     bouts_path = os.path.join(datadir, bouts_f)
#     all_profile_path = os.path.join(datadir, 'all_profile.csv')
#     omr_profile_path = os.path.join(datadir, 'omr_profile.csv')
#     calc_profiles(infile=bouts_ts_path, omrfile=omr_profile_path, allfile=all_profile_path)
#
#     # generate bout-level data
#     bouts_datafile(bouts_ts_path, bouts_path)


if __name__ == '__main__':
    def test():
        base_folder = '../data/expt'  # base folder
        all_subfolder = 'bout_test'  # subfolder for combined data from both procedures
        bouts_ts_f = 'bouts_ts.feather'  # filename for timeseries data including trajectory and bout info

        # bout summary files
        bouts_f = 'bouts_summ.feather'  # filename for output bout-level data
        bouts_sess_summ_f = "bouts_sess_summ.csv"  # filename for session-level bout summary data
        bouts_group_summ_f = "bouts_group_summ.csv"  # filename for group-level bout summary data

        base_folder = os.path.abspath(os.path.expanduser(base_folder))
        all_folder = os.path.join(base_folder, all_subfolder)

        process_bouts(datadir=all_folder, bouts_ts_f=bouts_ts_f, bouts_f=bouts_f, bouts_sess_summ_f=bouts_sess_summ_f,
                      bouts_group_summ_f=bouts_group_summ_f)

    test()
