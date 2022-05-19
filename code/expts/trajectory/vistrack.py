from math import sqrt, ceil
import os
import time

from matplotlib import gridspec

import matplotlib.pyplot as plt
import pandas as pd

from expts.trajectory.utils import save_figs


def get_data(inpath, summarypath=None):
    """Return DataFrames for the tracking data and summary
    """
    dpath = os.path.expanduser(inpath)
    print(f'reading tracking data from {dpath}')
    _, ext = os.path.splitext(inpath)
    if ext == '.csv':
        ddf = pd.read_csv(dpath)
    elif ext == '.feather':
        ddf = pd.read_feather(dpath)

    sdf = None
    if summarypath is not None:
        spath = os.path.expanduser(summarypath)
        print(f'reading summary data from {spath}')
        sdf = pd.read_csv(spath)

    return ddf, sdf


def add_step_type(df):
    ''' Return df with added column 'direction' indicating whether in forward trajectory (F),
    backward trajectory (B), or neither (N)

    Note: updated in place
    '''
    f_start = 70000  # when forward trial starts in ms
    arena_len = 300  # length of arena in mm
    rest_duration = 5000  # length of rest period between trials in ms

    df['direction'] = 'N'

    trial_duration = (arena_len / df['stimulus_speed']) * 1000

    f_end = f_start + trial_duration
    b_start = f_end + rest_duration
    b_end = b_start + trial_duration

    forward = (df['time'] >= f_start) & (df['time'] <= f_end)
    df.loc[forward, 'direction'] = 'F'

    backward = (df['time'] >= b_start) & (df['time'] <= b_end)
    df.loc[backward, 'direction'] = 'B'

    return df


def indiv_track_fig(df, *, height, ss, sid):
    """Return figure for tracking data from an individual session
    """
    grouped = df.groupby(['height', 'stimulus_speed', 'id'])

    #     for n, df in grouped:
    #         print(n)

    df = grouped.get_group((height, ss, sid))
    print(df)

    fig, ax = plt.subplots()

    ax.scatter(df['time'] / 1000, df['xpos'], s=1)
    # ax.plot(df['time'] / 1000, df['xpos'])
    #     ax.legend()
    ax.grid()
    ax.set_xlabel('time')
    ax.set_ylabel('x position (pixels')
    fig.suptitle(f'height {height} stimulus speed {ss} subject {sid}')
    ax.set_ylim(0, 1920)
    return fig


def track_figs(df, summary=None, **args):
    """Return figures showing tracking data for multiple sessions
    """
    # convert times to s
    df['time'] /= 1000
    if summary is not None:
        summ = summary.set_index(['Height', 'Speed', 'ID', 'Direction']).cat
    else:
        summ = None
    figs = []
    for (height, ss), gdf in df.groupby(['height', 'stimulus_speed']):
        fig = group_track_fig(gdf, height, ss, summary=summ, **args)
        figs.append(((height, ss), fig))
    return figs

    # return [ ((height, ss), group_traj_fig(gdf, summ, height, ss, direction))
    #          for ((height, ss), gdf ), ( _, sdf) in zip(gdata, gsumm) ]


def group_track_fig(df, height, stimspeed, *, summary=None, direction=None, **args):
    ''' Return figure showing the trajectories for all subjects with given height and stimulus speed.
    
    By default full trajectories are shown. If direction is 'F' or 'B' then only portions for the
    forward or backward traverses
    '''
    # selector = (df.height == height) & (df.stimulus_speed == stimspeed)
    # df = df.loc[selector, ['time', 'xpos', 'id', 'direction']]

    # trial_duration = df['stimulus_speed'].apply(f_trial_duration)
    # rest_duration = 5  # length of rest period between trials in seconds
    # f_start = 70
    # f_end = f_start + trial_duration
    # b_start = f_end + rest_duration
    # b_end = b_start + trial_duration
    # session_duration = b_end + rest_duration

    # trial_duration = (arena_len / stimspeed) * 1000
    # trial_duration = f_trial_duration(ss)
    #
    # f_start = 70  # when forward trial starts in ms
    # f_end = f_start + trial_duration
    # b_start = f_end + rest_duration
    # b_end = b_start + trial_duration
    # session_duration = b_end

    # print(f'direction {direction}')
    if direction == 'F':
        # duration = trial_duration
        figtype = 'forward trajectory'
    elif direction == 'B':
        figtype = 'backward trajectory'
    else:
        # duration = session_duration
        figtype = 'full session'

    # print(f'figtype {figtype}')
    groups = df.groupby('id', sort=False)
    nsubj = len(groups)
    print(nsubj, 'subjects')

    fsize = 15, 10
    fig = plt.figure(figsize=fsize)

    nrows = ncols = ceil(sqrt(nsubj))
    gs = gridspec.GridSpec(nrows, ncols)
    axes = [fig.add_subplot(gs[row, col]) for row in range(nrows)
            for col in range(ncols)]

    # set up the subplots with minimal decoration
    for ax in axes:
        ax.margins(0)
        ax.tick_params(
            axis='both',  # apply to both axes
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            left=False,
            labelbottom=False,  # labels along the bottom edge are off
            labelleft=False),

    for ax, (sid, gdf) in zip(axes, groups):
        cat = None
        if summary is not None:
            if direction == 'F':
                cat = summary[height, stimspeed, sid, 'for']
            elif direction == 'B':
                cat = summary[height, stimspeed, sid, 'rev']
            else:
                cat = (summary[height, stimspeed, sid, 'for'] +
                       summary[height, stimspeed, sid, 'rev'])

        # print('category', cat)

        track_plot(ax, gdf, sid, stimspeed, cat=cat, direction=None, **args)

    # place subplots subplots within 1x0.97 rectangle within the figure area
    # this leaves space above the subplots for a title (not supported by tight_layout)
    # set padding between subplots to 0.4 (as a proportion of font size)
    fig.tight_layout(h_pad=0.4, w_pad=0.4, rect=(0, 0, 1, 0.97))
    title = f'height {height} stimulus speed {stimspeed} - {figtype}'
    fig.text(0.3, 0.97, title, fontsize='large')

    print(title)
    return fig


def track_plot(ax, df, sid, ss, *, f_trial_duration, direction, cat=None):
    """Generate a tracking plot for a single session or trajectory within the given axes

    f_trial_duration: a function returning the trial duration given the stimulus speed
    cat: text indicating the trajectory or session categories
    """
    ymax, ymin = 0, 1920
    trial_duration = f_trial_duration(ss)
    rest_duration = 5  # length of rest period between trials in seconds
    f_start = 70
    f_end = f_start + trial_duration
    b_start = f_end + rest_duration
    b_end = b_start + trial_duration
    session_duration = b_end + rest_duration

    if direction == 'F':
        duration = trial_duration
        df = df[df['direction'] == 'F']
    elif direction == 'B':
        duration = trial_duration
        df['time'] -= b_start
        df = df[df['direction'] == 'B']
    else:
        duration = session_duration
        ax.vlines([f_start, f_end], ymin, ymax, colors=['green', 'green'])
        ax.vlines([b_start, b_end], ymin, ymax, colors=['purple', 'purple'])

    ax.plot(df['time'], df['xpos'], marker='.', markersize=1, linestyle='None')
    ax.grid()

    txt = f"{sid}"
    if cat is not None:
        txt += f'  {cat}'

    ax.text(0.02, 0.92, txt, transform=ax.transAxes)
    ax.set_ylim(0, 1920)
    ax.set_xlim(0, duration)


if __name__ == '__main__':
    inpath = r'~\data\ezfish\freeswim\pilot\fsm_track.feather'
    # summary file for the category information
    # summary_file = r'~\data\ezfish\expts\pilot\fsm_exp1_rep6_kv_pilot.csv'
    summary_file = None
    trackfigdir = r'~\data\ezfish\freeswim\pilot\temp\trackfigs'


    def trial_duration(stimulus_speed):
        """Return trial in duration in seconds given
        stimulus speed in mm/s
        """
        durations = {2: 150, 4: 75, 6: 50, 8: 37.5, 10: 30}
        return durations[stimulus_speed]


    # examples
    height = 'h4'
    ss = [8, 10]
    sids = [5, 6]

    pd.set_option('display.precision', 3)
    pd.set_option('display.expand_frame_repr', False)

    start = time.time()

    track_df, summary = get_data(inpath, summary_file)
    print(f'Read data and summary in  {time.time() - start :.1f} s')

    track_df = track_df[(track_df.stimulus_speed.isin(ss)) & (track_df.id.isin(sids))]

    track_df = add_step_type(track_df)

    # generate and save all figures
    figs = track_figs(track_df, summary=summary, f_trial_duration=trial_duration)
    save_figs(figs, trackfigdir)

    direction = 'F'
    # figs = track_figs(track_df, summary, direction)
    # save_figs(figs, trackfigdir, direction)

    direction = 'B'
    # figs = track_figs(track_df, summary, direction)
    # save_figs(figs, trackfigdir, direction)

    print(f'Elapsed time {time.time() - start :.1f} s')

    plt.show()
