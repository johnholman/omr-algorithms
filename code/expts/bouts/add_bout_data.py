# add additional bout data
import numpy as np
import pandas as pd

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


# def add_bout_speed(bout_df, dt):
#     """Add speed and other information for an individual bout"""
#
#     bout_num, subj_id = bout_df.iloc[0][['bout_num', 'id']]
#     print(f'id {subj_id} bout {bout_num}')
#
#     if bout_num == -1:  # ignore invalid bouts
#         df = bout_df
#     else:
#         # calculate step speeds and displacement over up to first 1s
#         v = np.abs(np.gradient(bout_df.xpos, dt))
#         # df = bout_df.assign(swim_speed=v)
#         tmax = 100
#         xstart = bout_df.iloc[0].xpos
#         xend = bout_df.iloc[-1].xpos if len(bout_df) < tmax else bout_df.iloc[tmax - 1].xpos
#         disp = abs(xend - xstart)
#
#         # bout peak speed
#         peak_speed = v.max()
#
#         # bout duration
#         bout_duration = len(bout_df) * dt
#
#         df = bout_df.assign(swim_speed=v, bout_displacement=disp, bout_peak_speed=peak_speed,
#                             bout_duration=bout_duration)
#
#         # add normalised speed for bouts with non-zero displacement
#         norm_speed = np.nan
#         ss = df.swim_speed[:tmax].sum()
#         if ss > 0:
#             norm_speed = df.swim_speed / ss
#         df = df.assign(bout_norm_speed=norm_speed)
#
#         # add initial speed over the first 10 timesteps (0.1s)
#         initial_steps = 10
#         initial_speed = np.nan
#         if len(bout_df) > initial_steps:
#             initial_speed = abs(bout_df.iloc[initial_steps].xpos - xstart) / (dt * initial_steps)
#         else:
#             # invalidate bout as it is shorter than 0.1s
#             df = df.assign(bout_num=-1)
#
#         # get mean speed over 50ms
#         mean_speed = ((bout_df.xpos - bout_df.xpos.shift(5)) / (5 * dt)).abs()
#         df = df.assign(mean_speed=mean_speed)
#
#         # mark timesteps where bout starts and ends according to the bout identification algorithm
#         events = np.zeros(len(df))
#         # mark first step as the start event (1)
#         events[0] = 1
#         # # mark first step with bout_id of -1 as the end event (2)
#         # active_steps = df.bout_id.argmin()
#         # events[active_steps] = 2
#         m = df.mean_speed.copy()
#         # find timestep with fastest mean speed
#         peak = m.argmax()
#         m[:peak] = 100
#         active_steps = (m < 5).argmax()
#         # if no active steps or peak is later than 0.5s consider that end could not be detected
#         if active_steps == 0 or peak > 50:
#             active_steps = np.nan
#         else:
#             events[active_steps] = 2
#         df = df.assign(bout_event=events, active_duration=active_steps * dt)
#         print(f'active steps: {active_steps}')
#
#         # invalidate bouts with very low initial speed
#         if initial_speed < 1.0:
#             df = df.assign(bout_num=-1)
#
#         df = df.assign(bout_initial_speed=initial_speed)
#
#         # add indicator for whether the bout is within an OMR trajectory
#         df = df.assign(omr_bout=((~df.prune) & (df.traj_id != -1)).all())
#
#     return df

# def add_bout_speed(bout_df, dt):
#     """Add speed and other information for an individual bout"""
#
#     bout_num, subj_id = bout_df.iloc[0][['bout_num', 'id']]
#     print(f'id {subj_id} bout {bout_num}')
#
#     if bout_num == -1:  # ignore invalid bouts
#         df = bout_df
#     else:
#         # calculate step speeds and displacement over up to first 1s
#         v = np.abs(np.gradient(bout_df.xpos, dt))
#         # df = bout_df.assign(swim_speed=v)
#         tmax = 100
#         xstart = bout_df.iloc[0].xpos
#         xend = bout_df.iloc[-1].xpos if len(bout_df) < tmax else bout_df.iloc[tmax - 1].xpos
#         disp = abs(xend - xstart)
#
#         # bout peak speed
#         peak_speed = v.max()
#
#         # bout duration
#         bout_duration = len(bout_df) * dt
#
#         df = bout_df.assign(swim_speed=v, bout_displacement=disp, bout_peak_speed=peak_speed,
#                             bout_duration=bout_duration)
#
#         # add normalised speed for bouts with non-zero displacement
#         norm_speed = np.nan
#         ss = df.swim_speed[:tmax].sum()
#         if ss > 0:
#             norm_speed = df.swim_speed / ss
#         df = df.assign(bout_norm_speed=norm_speed)
#
#         # add initial speed over the first 10 timesteps (0.1s)
#         initial_steps = 10
#         initial_speed = np.nan
#         if len(bout_df) > initial_steps:
#             initial_speed = abs(bout_df.iloc[initial_steps].xpos - xstart) / (dt * initial_steps)
#         else:
#             # invalidate bout as it is shorter than 0.1s
#             df = df.assign(bout_num=-1)
#
#         # get mean speed over 50ms
#         mean_speed = ((bout_df.xpos - bout_df.xpos.shift(5)) / (5 * dt)).abs()
#         df = df.assign(mean_speed=mean_speed)
#
#         # mark timesteps where bout starts and ends according to the bout identification algorithm
#         events = np.zeros(len(df))
#         # mark first step as the start event (1)
#         events[0] = 1
#         # # mark first step with bout_id of -1 as the end event (2)
#         # active_steps = df.bout_id.argmin()
#         # events[active_steps] = 2
#
#
#
#         m = df.mean_speed.copy()
#         m[:m.argmax()] = 100
#
#         # threshold 2 mm/s
#         active_steps = (m < 2).argmax()
#         if active_steps == 0:
#             active_steps = np.nan
#         else:
#             events[active_steps] = 2
#         df = df.assign(active_duration2=active_steps * dt)
#
#         # threshold 4 mm/s
#         active_steps = (m < 4).argmax()
#         if active_steps == 0:
#             active_steps = np.nan
#         else:
#             events[active_steps] = 4
#         df = df.assign(active_duration4=active_steps * dt)
#
#         # threshold 6 mm/s
#         active_steps = (m < 6).argmax()
#         if active_steps == 0:
#             active_steps = np.nan
#         else:
#             events[active_steps] = 6
#         df = df.assign(active_duration6=active_steps * dt)
#
#         df = df.assign(bout_event=events)
#
#         # invalidate bouts with very low initial speed
#         if initial_speed < 1.0:
#             df = df.assign(bout_num=-1)
#
#         df = df.assign(bout_initial_speed=initial_speed)
#
#         # add indicator for whether the bout is within an OMR trajectory
#         df = df.assign(omr_bout=((~df.prune) & (df.traj_id != -1)).all())
#
#     return df

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

        # get mean speed over 50ms
        mean_speed = ((bout_df.xpos - bout_df.xpos.shift(5)) / (5 * dt)).abs()
        df = df.assign(mean_speed=mean_speed)

        # mark timesteps where bout starts and ends according to the bout identification algorithm
        events = np.zeros(len(df))
        # mark first step as the start event (1)
        events[0] = 1
        # # mark first step with bout_id of -1 as the end event (2)
        # active_steps = df.bout_id.argmin()
        # events[active_steps] = 2



        m = df.mean_speed.copy()
        m[:m.argmax()] = 100
        active_steps = (m < 5).argmax()
        if active_steps == 0:
            active_steps = np.nan
        else:
            events[active_steps] = 2
        df = df.assign(bout_event=events, active_duration=active_steps * dt)
        print(f'active steps: {active_steps}')


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


if __name__ == '__main__':


    stimulus_speed = 4
    subj_id = 3
    # stimulus_speed = 12
    # subj_id = 5
    direction = 'F'
    inf = "../data/expt/or_test/bout_ids.feather"
    ids_sessf = "../data/expt/or_test/bout_ids_sess.feather"
    ts_sessf = "../data/expt/or_test/bout_ts_sess.feather"


    # example with 0 active duration
    subj_id = 7
    stimulus_speed = 10
    direction = 'B'
    seg_id = 1

    # example with 4s active duration
    subj_id = 72
    stimulus_speed = 4
    direction = 'F'
    seg_id = 0

    # OK examplse
    stimulus_speed = 12
    subj_id = 5
    direction = 'F'


    df = pd.read_feather(inf)
    df = df[(df.stimulus_speed == stimulus_speed) & (df.id == subj_id) & (df.direction == direction)]
    save_data(df, ids_sessf)
    add_bout_data(infile=ids_sessf, outfile=ts_sessf)

#    do the lot
#     inf = "../data/expt/or_test/bout_ids.feather"
#     outf = "../data/expt/or_test/bouts_ts.feather"
#     add_bout_data(infile=inf, outfile=outf)

    inf = "../data/expt/bf_test/bout_ids.feather"
    outf = "../data/expt/bf_test/bouts_ts.feather"
    add_bout_data(infile=inf, outfile=outf)

