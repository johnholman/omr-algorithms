import time

import numpy as np
import pandas as pd
from scipy import signal

from expts.utils.persist import load_data, save_data


def trim_ends(onsets, offsets, MIN_BOUTS=2):
    """" 
    Trim the head of onsets and tail of offsets to ensure proper pairing.
    """
    on_trimmed = onsets
    off_trimmed = offsets

    if len(onsets) >= MIN_BOUTS:
        if onsets[0] > offsets[0]:
            off_trimmed = np.delete(offsets, 0)
        if onsets[-1] > offsets[-1]:
            on_trimmed = np.delete(onsets, -1)

    return on_trimmed, off_trimmed


def filter_bouts(xpos, onsets, offsets, MIN_DUR=5, MIN_DIS=0.5):
    """
    Filter out invalid bouts which have duration less than 50ms and distance less than 0.5mm.
    """

    on_filtered = onsets
    off_filtered = offsets

    if len(onsets) == len(offsets):
        dur_diff = [(off - on) for on, off in zip(onsets, offsets)]
        dis_diff = [abs(xpos[off] - xpos[on]) for on, off in zip(onsets, offsets)]

        on_filtered = [el for i, el in enumerate(onsets) if dur_diff[i] > MIN_DUR if dis_diff[i] > MIN_DIS]
        off_filtered = [el for i, el in enumerate(offsets) if dur_diff[i] > MIN_DUR if dis_diff[i] > MIN_DIS]

    return on_filtered, off_filtered


def WL_method(df, fltr=True):
    """
    Algorithm for detecting bouts from 
    local maximas/minimas of instantaneous acceleration. 
    """
    onsets = np.array([])
    offsets = np.array([])

    # just interpolate the xpos column as this is all that is needed and
    # original code fails if time is given as a timedelta
    xposs = df.xpos.interpolate(method='linear').copy()
    xpos = np.array(xposs)

    # df = df.interpolate(method='linear').copy()
    # time = np.array(df.time)
    # xpos = np.array(df.xpos)
    # ypos = np.array(df.ypos)

    if len(xpos) > 150:

        h = signal.firwin(20, 0.02, window=('kaiser', 2))
        xsm = signal.filtfilt(h, 1, xpos, padlen=150)

        vel = abs(np.gradient(xsm, 0.01))
        accel = np.gradient(vel)

        onsets = signal.argrelextrema(accel, np.greater)[0]
        offsets = signal.argrelextrema(accel, np.less)[0]

        # trim 
        onsets, offsets = trim_ends(onsets, offsets)

        # filter 
        if fltr:
            onsets, offsets = filter_bouts(xpos, onsets, offsets)

    return onsets, offsets


def add_bouts(df, onsets, offsets):
    """
    Add bout start/total distance to each segment dataframe.
    """

    bout_id = np.full(df.shape[0], -1)
    tol_dist = np.full(df.shape[0], -1.)

    if len(onsets) == len(offsets):
        for i in range(len(onsets) - 1):
            bout_id[onsets[i]: offsets[i] + 1] = i
            tol_dist[onsets[i]: onsets[i + 1]] = abs(df['xpos'].iloc[onsets[i + 1] - 1] - df['xpos'].iloc[onsets[i]])

    df['bout_id'] = bout_id
    df['tol_dist'] = tol_dist
    return df


def get_bouts(df, boutID_method):
    """
    Get bouts for multiple sessions. Bout idenfication done per segment.
    """
    df = df.copy()
    df['bout_id'] = -1
    df['tol_dist'] = -1
    seg_dfs = []

    for (id, ss, direct, seg_id), seg_df in df.groupby(['id', 'stimulus_speed', 'direction', 'seg_id'],
                                                       sort=False, as_index=False):
        if direct != 'N' and seg_id != -1:
            print(f'BOUTS: id {id} ss {ss} dir {direct} seg id {seg_id}')
            ons, offs = boutID_method(seg_df)
            seg_df = add_bouts(seg_df, ons, offs)
            seg_dfs.append(seg_df)

    dfe = pd.concat(seg_dfs, sort=False)
    dfe = dfe.combine_first(df).copy()

    return dfe


def identify_bouts(inpath, outpath):
    start_time = time.time()

    df = load_data(inpath)
    # df = pd.read_feather(inpath)
    load_time = time.time()
    print(f'Load time {load_time - start_time :.1f} s')

    df_bout = get_bouts(df, WL_method)
    processed_time = time.time()
    print(f'Processing time {processed_time - load_time :.1f} s')

    save_data(df_bout, outpath)
    saved_time = time.time()
    print(f'Saving time {saved_time - processed_time :.1f} s')
