import pandas as pd


def extract(df, f_trial_duration):
    """ Return the given resampled free swimming data with added identification of traverses,
    segments and OMR-consistent trajectories
    """
    df = add_traverse_direction(df, f_trial_duration=f_trial_duration)
    df = add_segments(df).copy()
    dfe = add_trajectories(df)
    dfe = dfe.sort_values(by=['id', 'stimulus_speed', 'time']).reset_index(drop=True)
    return dfe


def add_traverse_direction(df, f_trial_duration):
    """ Return df with added column 'direction' indicating whether in forward trajectory (F),
    backward trajectory (B), or neither (N)

    Note: updated in place
    """
    print('defining traverses')
    rest_duration = pd.Timedelta(5, unit='s')  # length of rest period between trials
    trial_duration = pd.to_timedelta(df['stimulus_speed'].apply(f_trial_duration),
                                     unit='s')  # trajectory trial duration
    # trial_duration = pd.to_timedelta(arena_len / df['stimulus_speed'], unit='s')  # trajectory trial duration
    f_start = pd.Timedelta(70, unit='s')
    f_end = f_start + trial_duration
    b_start = f_end + rest_duration
    b_end = b_start + trial_duration

    df['direction'] = 'N'
    forward = (df['time'] >= f_start) & (df['time'] <= f_end)
    df.loc[forward, 'direction'] = 'F'

    backward = (df['time'] >= b_start) & (df['time'] <= b_end)
    df.loc[backward, 'direction'] = 'B'

    return df


def add_segments(df):
    """Return data for multiple sessions with segment id column added
    """
    print('extracting segments')
    df = df.groupby(['id', 'stimulus_speed', 'direction'],
                    group_keys=False, sort=False).apply(add_segments_to_session)
    return df


def add_segments_to_session(trav_df):
    """Return data for a single traverse with added column giving segment ids
    """
    trav_df = trav_df.copy()
    inseg = trav_df.xpos.notna()
    diffs = inseg.astype(int).diff()
    diffs.iat[0] = 0
    if not inseg.iat[0]:
        diffs.iat[1] = 0
    seg_ids = diffs.astype(int).clip(0).cumsum().where(inseg, -1)
    trav_df['seg_id'] = seg_ids
    return trav_df


def add_trajectories(df):
    """Return data for multiple sessions with added column giving trjectory ids
    """
    print('extracting trajectories')
    df['traj_id'] = -1
    seg_dfs = []
    for (id, ss, direct, seg_id), seg_df in df.groupby(['id', 'stimulus_speed', 'direction', 'seg_id'], sort=False,
                                                       as_index=False):
        print(f'id {id} ss {ss} dir {direct} seg id {seg_id}')
        # seg_df.set_index('time')
        seg_df = seg_df.copy()
        if direct != 'N' and seg_id != -1:
            traj_id_ts, f_slow, f_fast, b_slow, b_fast = extract_traj(seg_df, direct)
            seg_df['traj_id'] = traj_id_ts
            seg_df['f_slow'] = f_slow
            seg_df['f_fast'] = f_fast
            seg_df['b_slow'] = b_slow
            seg_df['b_fast'] = b_fast
        # seg_df.reset_index()
        seg_dfs.append(seg_df)
    dfe = pd.concat(seg_dfs, sort=False)
    return dfe


def extract_traj(seg_df, direction):
    """ Return data for a single segment adding trajectory ids
    """
    # print(f'extract_traj receives\n {seg_df.head(1)}')

    # negate x position to simulate continued movement in same direction for the
    # backward trajectory
    seg = seg_df.xpos if direction == 'F' else -seg_df.xpos
    # print(f'extract traj from seg\n{seg.head(1)}')
    # take exponential moving average with slow and fast decay
    f_slow = seg.ewm(alpha=0.002, min_periods=50).mean()
    f_fast = seg.ewm(alpha=0.05, min_periods=50).mean()

    # reverse time and take EMA
    b = seg.sort_index(ascending=False)
    b_slow = b.ewm(alpha=0.002, min_periods=50).mean()
    b_fast = b.ewm(alpha=0.05, min_periods=50).mean()

    # condition for upward trend
    up = (f_slow < f_fast) & (b_slow > b_fast)
    traj_id_ts = (up.astype(int)  # 1 for up, 0 otherwise
                  .diff()  # to up transitions marked with 1.0, from up with -1.0
                  .clip(0)  # rectify out from up transitions
                  .cumsum()  # integrate to number the up transitions
                  .subtract(1)  # adjust to make ids zero-based
                  .where(up, -1)  # indicate that not an OMR trajectory timestep in not in an upward trend
                  .astype(int))  # convert to integer now we no longer have the initial NaN

    # restore EMA distances for the backward trajectory
    if direction == 'B':
        f_slow = -f_slow
        f_fast = -f_fast
        b_slow = -b_slow
        b_fast = -b_fast

    return traj_id_ts, f_slow, f_fast, b_slow, b_fast


def prune(df, xmax, xmin, min_seg_dur, min_traj_dur, min_traj_speed):
    """Return data for multiple sessions after pruning segments and trajectories

    Segment ids for segments shorter than the minimum duration are set to -1
    Trajectory id for trajectories shorter than minimums duration or min average speed
    are set to -1
    """
    seg_limit = pd.Timedelta(min_seg_dur, unit='s')
    traj_duration_limit = pd.Timedelta(min_traj_dur, unit='s')

    # drop EMA columns if present to save space
    if 'f_slow' in df.columns:
        df = df.drop(['f_slow', 'f_fast', 'b_slow', 'b_fast'], axis=1)

    # # duplicate existing seg_id and traj_id columns
    # df['seg_id_orig'] = df['seg_id']
    # df['traj_id_orig'] = df['traj_id']

    # add column to indicate whether timestep should be pruned
    df['prune'] = False

    print('pruning after boundary reached')
    df = prune_boundary(df, xmax, xmin)

    # workdir = r'~\data\ezfish\expts\baseline\temp'
    # save_data(df, workdir, "preprune.csv")

    print('pruning segments')
    segs = df.groupby(['id', 'stimulus_speed', 'direction', 'seg_id', 'prune'], sort=False, as_index=False)
    pruned_df = pd.concat([prune_seg(seg_df, seg_limit, *keys) for keys, seg_df in segs])

    # save_data(pruned_df, workdir, "segprune.csv")

    print('pruning trajectories')
    trajs = pruned_df.groupby(['id', 'stimulus_speed', 'direction', 'seg_id', 'traj_id', 'prune'], sort=False,
                              as_index=False)
    pruned_df = pd.concat([prune_traj(traj_df, *keys, traj_duration_limit, min_traj_speed) for keys, traj_df in trajs])
    pruned_df = pruned_df.sort_values(by=['id', 'height', 'stimulus_speed', 'time']).reset_index(drop=True)

    # # attempt to replicate original file
    # p1df = pruned_df.copy()
    # p1df.loc[p1df.prune == True, ['seg_id', 'traj_id']] = -1
    # p1df = p1df.drop('prune', axis=1)

    return pruned_df


def prune_seg(seg_df, seg_limit, id, ss, direct, seg_id, prune):
    """Return pruned data for a single segment
    """
    if seg_id != -1 and not prune and ((seg_df.time.max() - seg_df.time.min()) < seg_limit):
        print(f'subj {id} speed {ss} trajectory {direct}: pruning seg {seg_id} ')
        seg_df = seg_df.copy()
        # seg_df['seg_id'] = -1
        # seg_df['traj_id'] = -1
        seg_df['prune'] = True
    return seg_df


def prune_traj(traj_df, id, ss, direct, seg_id, traj_id, prune, traj_duration_limit, traj_speed_limit):
    """Return pruned data for a single trajectory
    """
    if seg_id != -1 and traj_id != -1 and not prune:
        traj_duration = traj_df.time.iat[-1] - traj_df.time.iat[0]
        traj_disp = abs(traj_df.xpos.iat[-1] - traj_df.xpos.iat[0])
        traj_speed = traj_disp / traj_duration.total_seconds()
        if traj_duration < traj_duration_limit or traj_speed < traj_speed_limit:
            print(f'subj {id} speed {ss} trajectory {direct}: pruning seg {seg_id} traj {traj_id}')
            traj_df = traj_df.copy()
            # traj_df['traj_id'] = -1
            traj_df['prune'] = True
    return traj_df


def prune_boundary(df, xmax, xmin):
    """
    Return data with segment and trajectories set to -1 for times after reaching the boundary

    For forward traverses, the boundary position is xmax; for backward
    ones xmin.
    """

    # add column to indicate whether fish has reached goal for current trial
    df['reached_goal'] = False

    margin = 10  # distance within the arena from the boundary before checking progress
    slist = []
    for (id, h, ss), sess_df in df.groupby(['id', 'height', 'stimulus_speed']):
        print(f'boundary pruning for id {id} height {h} stim speed {ss}')
        sess_df = sess_df.copy()
        margin_time = sess_df[(sess_df.direction == 'F') & (sess_df.xpos < xmax - margin)].time.min()
        forward_time_reached = sess_df[(sess_df.direction == 'F') &
                                       (sess_df.time > margin_time) &
                                       (sess_df.xpos > xmax)].time.min()
        # sess_df.loc[(sess_df.direction == 'F') & (sess_df.time >= forward_time_reached), ['seg_id', 'traj_id']] = -1
        sess_df.loc[(sess_df.direction == 'F') & (sess_df.time >= forward_time_reached), ['prune']] = True
        sess_df.loc[(sess_df.direction == 'F') & (sess_df.time >= forward_time_reached), ['reached_goal']] = True

        margin_time = sess_df[(sess_df.direction == 'B') & (sess_df.xpos > xmin + margin)].time.min()
        backward_time_reached = sess_df[(sess_df.direction == 'B')
                                        & (sess_df.time > margin_time)
                                        & (sess_df.xpos < xmin)].time.min()
        # sess_df.loc[(sess_df.direction == 'B') & (sess_df.time >= backward_time_reached), ['seg_id', 'traj_id']] = -1
        sess_df.loc[(sess_df.direction == 'B') & (sess_df.time >= backward_time_reached), ['prune']] = True
        sess_df.loc[(sess_df.direction == 'B') & (sess_df.time >= backward_time_reached), ['reached_goal']] = True
        slist.append(sess_df)
    dfp = pd.concat(slist)
    return dfp

if __name__ == '__main__':
    def test():
        from expts.utils.persist import load_data
        resample_fname = 'resample.feather'
        fname = "../data/expt/bf/bouts_ts.feather"

        resample_path = os.path.join(datadir, resample_fname)

        resample_df = load_data(resample_path)

        extract_df = extract(resample_df, f_trial_duration=trial_duration)