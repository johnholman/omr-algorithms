import numpy as np
import pandas as pd

from simulator.reporting.figs import select_period


def summarise_groups_for_comparison(df, period=None, **args):
    """ Return group-level summary including keys for comparison with experimental data

    This runs summarise_groups() then adds height_category and expt_condition variables for matching
    to the corresponding experimental condition
    """
    summary_df = summarise_groups(df, period=period, **args)

    height_category = summary_df['height'].map({8.0: 'h1', 32.0: 'h4', 56.0: 'h7'})

    expt_condition = height_category + '_' + summary_df.stimulus_speed.apply(lambda x: f'{x:.2f}')
    summary_df = summary_df.assign(height_category=height_category, expt_condition=expt_condition)

    return summary_df


def summarise_groups(df, *, indiv_bout_stats=False, phases=None, period=None, terminal_duration=None,
                     valid_proportion=0.0, **_args):
    """ Return summary_df data for each group, including bout analysis.

    period or terminal_duration specify the period within the session to be included in the summary

    Groups with less than valid_proportion of subjects having valid records are marked as invalid. By default all groups
    are considered to have valid data.
    """

    # support terminal_duration parameter for backwards compatibility
    if terminal_duration is not None:
        period = -terminal_duration

    # select period to summarise
    if period is not None:
        df = select_period(df, period)

    # select only phases to be included
    if phases is not None:
        df = df[df['phase_id'].isin(phases)]

    # summarise over groups, phases and subjects
    groupcols = ['group_id', 'phase_id', 'subj_id']

    # take the mean for numeric columns, otherwise the value from the first row
    # this assumes that non-numeric columns will have the same values (e.g. be values of independent variables)
    # also note that for some reason None is translated to nan
    spec = {col: 'mean' if pd.api.types.is_numeric_dtype(df[col]) else 'first' for col in df.columns if
            col not in groupcols}
    summary_df = df.groupby(groupcols, sort=False).agg(spec)

    summary_df = add_derived_variables(summary_df)

    # take means over subjects for each group and phase
    summary_df = summary_df.groupby(['group_id', 'phase_id'], sort=False).mean()

    summary_df = summary_df.assign(omr_rmse=np.sqrt(summary_df.omr_mse))

    # bout analysis
    bout_stats = terminating_bout_stats if 'swimming' in df else nonterminating_bout_stats
    bout_summary_indiv = df.groupby(['group_id', 'phase_id', 'subj_id'], sort=False).apply(bout_stats)
    if indiv_bout_stats:
        print(f'overall bout statistics for each subject\n{bout_summary_indiv}\n')

    # summarise bout data over subjects
    spec = {col: (col, 'mean') for col in bout_summary_indiv}
    spec['nvalidrec'] = ('bout_init_speed', 'count')  # number of subjects with valid data, i.e. not NaN initial speed
    spec['nrec'] = ('bout_init_speed', 'size')

    # print(f'spec: {spec}')
    bout_summary = bout_summary_indiv.groupby(['group_id', 'phase_id']).agg(**spec)

    #
    is_valid = (bout_summary.nvalidrec > 0) & (bout_summary.nvalidrec / bout_summary.nrec >= valid_proportion)
    bout_summary = bout_summary.assign(is_valid=is_valid)

    #     print(f'bout summary_df \n{bout_summary}\n')

    # join into a single table to give the overall session summary_df
    summary_df = summary_df.join(bout_summary, on=['group_id', 'phase_id']).reset_index()

    return summary_df


def add_derived_variables(df):
    """ Return the given dataframe with some added derived variables

    df is expected to contain the standard OMR variables swim_speed, swim_speed_req and height
    """
    omr_ratio = df.swim_speed / df.swim_speed_req
    baseline_flow = round(df.swim_speed_req / df.height, 5)
    ssbf_ratio = df.swim_speed / baseline_flow
    omr_mse = ((df.swim_speed - df.swim_speed_req) / df.swim_speed_req) ** 2

    return df.assign(omr_ratio=omr_ratio, baseline_flow=baseline_flow,
                     ssbf_ratio=ssbf_ratio, omr_mse=omr_mse)


def terminating_bout_stats(df):
    #     print(df.head())
    bout_steps = 0
    total_steps = len(df)
    total_effort = 0
    in_bout = False
    for rec in df.itertuples():
        if rec.swimming:
            if not in_bout:  # new bout detected
                in_bout = True
            bout_steps += 1
            total_effort += rec.motor_output
        else:
            in_bout = False

    dt = df.dt.iat[0]
    Ke = df.Ke.iat[0]
    total_time = dt * total_steps
    num_bouts = df.start_bout.sum()
    bout_rate = num_bouts / total_time
    total_bout_duration = bout_steps * dt
    #     mean_duration = bout_steps*dt/num_bouts if num_bouts > 0 else 0
    bout_duration = total_bout_duration / num_bouts if num_bouts > 0 else 0
    interbout_duration = (total_time - total_bout_duration) / num_bouts if num_bouts > 0 else 0
    mean_rest_rate = 1 / interbout_duration if interbout_duration > 0 else 0
    bout_effort = total_effort / bout_steps if bout_steps > 0 else 0
    bout_speed = bout_effort * Ke
    duty_cycle = bout_steps / total_steps
    swim_drive = df.loc[df['swimming'], 'motor_drive'].mean()
    rest_drive = df.loc[~df['swimming'], 'motor_drive'].mean()

    data = {'num_bouts': num_bouts,
            'bout_rate': bout_rate,
            'bout_duration': bout_duration,
            'bout_effort': bout_effort,
            'bout_speed': bout_speed,
            'interbout_duration': interbout_duration,
            'mean_rest_rate': mean_rest_rate,
            'duty_cycle': duty_cycle,
            'swim_drive': swim_drive,
            'rest_drive': rest_drive,
            }
    return pd.Series(data)


def nonterminating_bout_stats(traj_df, initial_duration=0.1, premature_threshold=10, subliminal_threshold=3.0,
                              required_valid=0.0):
    # calculate number of steps in the initial duration over which initial bout speed is averaged
    dt = traj_df.iloc[0].loc['dt']
    initial_steps = int(initial_duration / dt)
    # print(f'{initial_steps=}')

    # select timesteps when a bout begins
    starts = traj_df[traj_df.start_bout]
    total_bouts = len(starts)

    # disregard an initial bout if starts on first timestep as we need the
    # previous step to check whether premature
    if total_bouts > 0 and starts.index[0] == traj_df.index[0]:
        starts = starts.iloc[1:]

    valid_init_speeds = []
    init_speeds = []
    num_subliminal = 0
    num_premature = 0
    # process each bout
    for start in starts.index[:-1]:
        if traj_df['swim_speed'].loc[start - 1] > premature_threshold:
            num_premature += 1
        # initial bout speed is averaged over the initial duration
        init_speed = traj_df['swim_speed'].loc[start:start + initial_steps - 1].mean()

        # bout is filtered as invalid if initial speed is less than the subliminal threshold
        if init_speed < subliminal_threshold:
            num_subliminal += 1
        else:
            # sufficiently strong bouts contribute towards bout rate and initial speed
            valid_init_speeds.append(init_speed)

        init_speeds.append(init_speed)

    num_valid_bouts = len(valid_init_speeds)
    num_unfiltered_bouts = len(init_speeds)

    traj_dist = traj_duration = None
    if num_unfiltered_bouts > 0:
        first = traj_df.loc[starts.index[0]]
        last = traj_df.loc[starts.index[-1] - 1]
        traj_dist = last.position - first.position
        traj_duration = last.time - first.time

    # if there are no valid bouts take the rate to be zero and initial speed as unknown
    if num_valid_bouts == 0 or num_valid_bouts / num_unfiltered_bouts < required_valid:
        bout_rate = 0.0
        bout_init_speed = np.nan
        bout_dist = np.nan
    else:
        bout_init_speed = sum(valid_init_speeds) / num_valid_bouts
        bout_rate = num_valid_bouts / traj_duration
        bout_dist = traj_dist / num_valid_bouts

    if num_unfiltered_bouts == 0:
        bout_rate_unfiltered = 0.0
        bout_init_speed_unfiltered = np.nan
    else:
        bout_init_speed_unfiltered = sum(init_speeds) / num_unfiltered_bouts
        bout_rate_unfiltered = num_unfiltered_bouts / traj_duration

    # print(f'{total_bouts=} {num_valid_bouts=} {num_premature=} {num_subliminal=}'
    #       f'{traj_duration=} {traj_dist=} {bout_rate=} {bout_dist=}')

    data = pd.Series({'total_bouts': total_bouts,
                      'num_subliminal': num_subliminal,
                      'num_premature': num_premature,
                      'num_bouts': num_valid_bouts,
                      'bout_rate': bout_rate,
                      'bout_dist': bout_dist,
                      'bout_init_speed': bout_init_speed,
                      'bout_rate_unfiltered': bout_rate_unfiltered,
                      'bout_init_speed_unfiltered': bout_init_speed_unfiltered,
                      })
    return data


def indiv_analysis(data, *, group_id, subj_id, **_args):
    md, df = data
    name = md.get('name')
    print(f'*** individual report for {name} group {group_id} subj {subj_id}')
    bout_stats = terminating_bout_stats if 'swimming' in df else nonterminating_bout_stats
    summary = bout_stats(df)
    print(summary)
