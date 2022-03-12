# process consolidated tracking data from the OR experiment to extract OMR trajectories
import os
import time

import matplotlib.pyplot as plt
import pandas as pd

from expts.trajectory.extract import prune, extract
from expts.trajectory.resample import rescale, resample
from expts.trajectory.vistrack import indiv_track_fig
from expts.trajectory.vistraj import traj_fig
from expts.utils.persist import save_data, load_data


def extract_trajectories(datadir, tracked_fname, traj_ts_f, trial_duration, examples=None):
    """
    Extract trajectories from the tracked position data

    :param datadir: data directory
    :param tracked_fname: filename for input tracked data
    :param traj_ts_f: filename for saving output trajectory data
    :param trial_duration: function mapping stimulus speed to trial duration
    :param examples: dict giving values of height, stimulus speed and subject id to include (default: include all)

    The tracked data is first rescaled and resampled, then trajectories are extracted and pruned.
    Datafiles for intermediate steps are also saved.
    """
    start_time = time.time()

    rescale_fname = 'rescale.feather'
    resample_fname = 'resample.feather'
    traj_noprune_fname = 'traj_noprune.feather'

    tracked_path = os.path.join(datadir, tracked_fname)
    rescale_path = os.path.join(datadir, rescale_fname)
    resample_path = os.path.join(datadir, resample_fname)
    extract_path = os.path.join(datadir, traj_noprune_fname)
    traj_path = os.path.join(datadir, traj_ts_f)

    if examples:  # OR example
        height = examples['height']
        ss = examples['ss']
        sids = examples['sids']
    else:
        height = ss = sids = None

    # resample and rescale
    if tracked_path.endswith('.feather'):
        track_df = pd.read_feather(tracked_path)
    else:
        track_df = pd.read_csv(tracked_path)
    print(f'loaded track data from {tracked_path}:\n{track_df.head(2)}')

    # if looking at just the example select out data of interest
    if examples:
        track_df = track_df[(track_df.stimulus_speed.isin(ss)) & (track_df.id.isin(sids))]

        # track data plot
        for stimspeed in ss:
            for sid in sids:
                indiv_track_fig(track_df, height=height, sid=sid, ss=stimspeed)

    rescale_df = rescale(track_df)
    save_data(rescale_df, rescale_path)
    resample_df = resample(rescale_df)
    print(f'after resampling and rescaling:\n{resample_df.head(2)}\n')
    save_data(resample_df, resample_path)

    # identify traverses and extract segments and trajectories
    resample_df = load_data(resample_path)

    # if looking at just the example select out data of interest
    if examples:
        resample_df = resample_df[(resample_df.stimulus_speed.isin(ss)) & (resample_df.id.isin(sids))]

    extract_df = extract(resample_df, f_trial_duration=trial_duration)
    print(f'after extracting segments and trajectories:\n{extract_df.head(2)}\n')
    save_data(extract_df, extract_path)

    if examples:
        for stimspeed in ss:
            for sid in sids:
                traj_fig(extract_df, height=height, sid=sid, ss=stimspeed, direction=None,
                         show_ema=True, f_trial_duration=trial_duration)

    # prune segment and trajectory fragments and traverses after reaching boundary
    extract_df = load_data(extract_path)

    traj_df = prune(extract_df, xmax=320, xmin=50, min_seg_dur=1, min_traj_dur=1, min_traj_speed=0.5)
    print(f'after boundary and fragment pruning:\n{traj_df.head(2)}\n')
    save_data(traj_df, traj_path)

    # for stimspeed in ss:
    #     for sid in sids:
    #         traj_fig(traj_df, height=height, sid=sid, ss=stimspeed, f_trial_duration=trial_duration)

    print(f'Processing time {time.time() - start_time :.1f} s')

    # if show_figs:
    #     # generate and save all track figures by condition
    #     figs = track_figs(track_df, f_trial_duration=trial_duration)
    #     save_figs(figs, trackfigdir)
    #
    #     # generate and save all trajectory figures by condition
    #     accept = summary_df.set_index(['Height', 'Speed', 'ID', 'Direction']).accept
    #     figs = traj_figs(traj_df, accept_summary=accept, f_trial_duration=trial_duration)
    #     save_figs(figs, trajfigdir)

    print(f'Total time {time.time() - start_time :.1f} s')


def test():
    datadir = '~/data/ezfish/analysis/ortest'
    track_fname = 'tracked.feather'
    traj_fname = 'traj.feather'

    pd.set_option('display.precision', 5)
    pd.set_option('display.expand_frame_repr', False)
    pd.options.display.max_rows = 200

    # def trial_duration(stimulus_speed):
    #     """Return trial duration in seconds given stimulus speed in mm/s
    #     """
    #     durations = {2: 150, 4: 75, 6: 50, 8: 37.5, 10: 30}
    #     return durations[stimulus_speed]

    def trial_duration(_ss):
        return 60

    # OR example
    # height = 'h1'
    # sids = [5, 6, 7]
    # ss = [4, 8, 12]

    # height = 'h4'
    # sids  = [47, 48, 49]
    # ss = [4, 8, 12]

    height = 'h7'
    sids = [28, 29, 30]
    ss = [4, 8, 12]

    examples = dict(height=height, ss=ss, sids=sids)

    extract_trajectories(datadir, track_fname, traj_fname, trial_duration, examples=examples)


if __name__ == '__main__':
    test()
    plt.show()
