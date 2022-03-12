# add additional bout data
import numpy as np

from expts.utils.persist import load_data, save_data


def add_bout_nums(df):
    """Return table with added bout numbers and step numbers for multiple sessions
    """
    df = df.groupby(['id', 'height', 'stimulus_speed', 'direction', 'seg_id'], group_keys=False).apply(
        add_seg_bout_nums)
    return df


def add_seg_bout_nums(seg_df):
    """Add bout_num and bout_step for all bouts in a segment

    The initial portion of the segment before the first bout start event are ignored, and
    the last bout in the segment is invalidated as time to next bout and displacement are unknown
    """
    print(f'segment {seg_df.name}')
    step_nums = []
    bout_nums = []
    step_num = -1
    bout_num = -1
    last_bout_id = -1
    for rec in seg_df.itertuples():
        bout_id = rec.bout_id
        if bout_id != last_bout_id and bout_id >= 0:
            # start of new bout
            bout_num += 1
            step_num = 0
        else:
            step_num += 1
        bout_nums.append(bout_num)
        step_nums.append(step_num)
        last_bout_id = bout_id
    # print(f'{bout_num=}')
    seg_df = seg_df.assign(bout_num=bout_nums, step_num=step_nums)

    # invalidate the last bout as it may extend beyond this segment
    seg_df.loc[seg_df.bout_num == bout_num, 'bout_num'] = -1

    return seg_df


def add_speed(df, dt):
    """Return data with added speed and other information for all bouts in the given data"""

    df = df.groupby(['id', 'height', 'stimulus_speed', 'direction', 'seg_id', 'bout_num'], group_keys=False).apply(
        add_bout_speed, dt)
    df = df.assign(omr_bout=df.omr_bout.fillna(False))

    # invalidate step numbers for all invalid bouts
    df.loc[df.bout_num == -1, 'step_num'] = -1

    return df


def add_bout_speed(bout_df, dt):
    """Add speed and other information for an individual bout"""

    bout_num, subj_id = bout_df.iloc[0][['bout_num', 'id']]
    print(f'id {subj_id} bout {bout_num}')

    if bout_num == -1:  # ignore invalid bouts
        df = bout_df
    else:
        # calculate step speeds and displacement over up to first 1s
        v = np.abs(np.gradient(bout_df.xpos, dt))
        # df = bout_df.assign(swim_speed=v)
        tmax = 100
        xstart = bout_df.iloc[0].xpos
        xend = bout_df.iloc[-1].xpos if len(bout_df) < tmax else bout_df.iloc[tmax - 1].xpos
        disp = abs(xend - xstart)

        # bout peak speed
        peak_speed = v.max()

        # bout duration
        bout_duration = len(bout_df) * dt

        df = bout_df.assign(swim_speed=v, bout_displacement=disp, bout_peak_speed=peak_speed,
                            bout_duration=bout_duration)

        # add normalised speed for bouts with non-zero displacement
        norm_speed = np.nan
        ss = df.swim_speed[:tmax].sum()
        if ss > 0:
            norm_speed = df.swim_speed / ss
        df = df.assign(bout_norm_speed=norm_speed)

        # add initial speed over the first 10 timesteps (0.1s)
        initial_steps = 10
        initial_speed = np.nan
        if len(bout_df) > initial_steps:
            initial_speed = abs(bout_df.iloc[initial_steps].xpos - xstart) / (dt * initial_steps)
        else:
            # invalidate bout as it is shorter than 0.1s
            df = df.assign(bout_num=-1)

        # invalidate bouts with very low initial speed
        if initial_speed < 1.0:
            df = df.assign(bout_num=-1)

        df = df.assign(bout_initial_speed=initial_speed)

        # add indicator for whether the bout is within an OMR trajectory
        df = df.assign(omr_bout=((~df.prune) & (df.traj_id != -1)).all())

    return df


def add_bout_data(*, infile, outfile):
    """Add additional bout data to the given data

    indir: directory for input data
    infile: input data filename
    outdir: directory for output data
    outfile: output data filename
    """
    df = load_data(infile)
    print('adding bout and step numbers')
    df = add_bout_nums(df)

    # sort data to restore the temporal order of events within sessions
    # as grouping collects together all invalid segments etc in the same group
    df = df.sort_values(['id', 'height', 'stimulus_speed', 'time'])
    dt = 0.01
    print('adding bout speeds etc')
    df = add_speed(df, dt)
    df = df.sort_values(['id', 'height', 'stimulus_speed', 'time'])

    print(df.head())

    save_data(df, outfile)
