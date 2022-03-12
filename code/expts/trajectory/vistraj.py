from math import ceil, sqrt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import gridspec


def traj_figs(df, summary=None, direction=None, accept_summary=None, **args):
    """Return figures showing trajectories for multiple sessions
    """
    # convert timedeltas to seconds expressed as float since matplotlib seems to have
    # difficulty otherwise
    df['time'] = pd.to_numeric(df['time']) / 1000000000

    figs = []
    for (height, ss), gdf in df.groupby(['height', 'stimulus_speed']):
        fig = group_traj_fig(gdf, height, ss, direction, summary, accept_summary, **args)
        figs.append(((height, ss), fig))
    return figs


def group_traj_fig(df, height, stimspeed, direction=None, summary=None, accept_summary=None, **args):
    ''' Return figure showing the trajectories for all subjects with given height and stimulus speed.

    By default full trajectories are shown. If direction is 'F' or 'B' then only portions for the
    forward or backward traverses
    '''
    if direction == 'F':
        figtype = 'forward trajectory'
    elif direction == 'B':
        figtype = 'backward trajectory'
    else:
        figtype = 'full session'

    print(f'figtype {figtype}')

    groups = df.groupby('id', sort=False)
    nsubj = len(groups)
    print(nsubj, 'subjects')

    fsize = 18, 12

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

        if summary is not None:
            if direction == 'F':
                cat = summary[height, stimspeed, sid, 'for']
            elif direction == 'B':
                cat = summary[height, stimspeed, sid, 'rev']
            else:
                cat = (summary[height, stimspeed, sid, 'for'] +
                       summary[height, stimspeed, sid, 'rev'])
        else:
            cat = None

        if accept_summary is not None:
            if direction == 'F':
                accept = accept_label(height, stimspeed, sid, 'for', accept_summary)
            elif direction == 'B':
                accept = accept_label(height, stimspeed, sid, 'rev', accept_summary)
            else:
                accept = (f"OK? {accept_label(height, stimspeed, sid, 'for', accept_summary)}"
                          f" {accept_label(height, stimspeed, sid, 'rev', accept_summary)}")
        else:
            accept = None

        traj_plot(ax, gdf, sid, stimspeed, cat=cat, accept=accept, direction=direction, **args)

    # place subplots subplots within 1x0.97 rectangle within the figure area
    # this leaves space above the subplots for a title (not supported by tight_layout)
    # set padding between subplots to 0.4 (as a proportion of font size)
    fig.tight_layout(h_pad=0.4, w_pad=0.4, rect=(0, 0, 1, 0.97))
    title = f'height {height} stimulus speed {stimspeed} - {figtype}'
    fig.text(0.3, 0.97, title, fontsize='large')
    # fig.autofmt_xdate()

    print(title)
    return fig


def traj_plot(ax, df, sid, ss, *, f_trial_duration, cat=None, accept=None, direction=None, show_ema=False):
    """Plot trajectories from a single trajectory or session identified by subject id and
    stimulus speed

    f_trial_duration: a function returning the trial duration given the stimulus speed
    cat: text indicating the trajectory or session categories
    accept: text indicating whether the traverses are accepted
    """
    arena_full_len = 370
    ax.set_ylim((0, arena_full_len))

    arena_len = 300  # length of central arena in mm
    rest_duration = 5  # length of rest period between trials in seconds
    # trial_duration = arena_len / ss  # trajectory trial duration
    # trial_duration = 60  # trajectory trial duration
    trial_duration = f_trial_duration(ss)
    f_start = 70
    f_end = f_start + trial_duration
    b_start = f_end + rest_duration
    b_end = b_start + trial_duration
    session_duration = b_end + rest_duration

    # pixmarg = 250
    # ymin = pixmarg
    # ymax = 1920 - pixmarg

    marg = 50
    ymin = marg
    ymax = arena_full_len - marg

    # print(f'direction {direction}')
    if direction == 'F':
        duration = trial_duration
        figtype = 'forward trajectory'
        df['time'] -= f_start
        df = df[df['direction'] == 'F']
        ax.hlines([ymin, ymax], 0, duration, colors=['green', 'green'])
    elif direction == 'B':
        duration = trial_duration
        figtype = 'backward trajectory'
        df['time'] -= b_start
        df = df[df['direction'] == 'B']
        ax.hlines([ymin, ymax], 0, duration, colors=['green', 'green'])
    else:
        duration = session_duration
        ax.vlines([f_start, f_end], ymin, ymax, colors=['green', 'green'])
        ax.vlines([b_start, b_end], ymin, ymax, colors=['purple', 'purple'])
        ax.hlines([ymin, ymax], f_start, f_end, colors=['green', 'green'])
        ax.hlines([ymin, ymax], b_start, b_end, colors=['purple', 'purple'])

        figtype = 'full session'

    ax.set_xlim((0, duration))

    print(f'plotting sid {sid} from\n{df.head(1)}')
    for (direct, seg_id), seg_df in df.groupby(['direction', 'seg_id'], sort=False):
        ax.plot(seg_df['time'], seg_df['xpos'], linestyle='None', marker='.',
                color=seg_col(direct, seg_id))
        if show_ema:
            ax.plot(seg_df['time'], seg_df['b_slow'], color='pink')
            ax.plot(seg_df['time'], seg_df['f_slow'], color='aquamarine')
            ax.plot(seg_df['time'], seg_df['b_fast'], color='darkred')
            ax.plot(seg_df['time'], seg_df['f_fast'], color='darkgreen')

        for traj_id, tdf in seg_df.groupby('traj_id', sort=False):
            if traj_id != -1:
                print(f'plotting trajectory {direct} seg {seg_id} traj {traj_id}')
                ax.plot(tdf['time'], tdf['xpos'], color=traj_col(traj_id))
    ax.grid()

    txt = f"{sid}"
    if cat is not None:
        txt += f'  {cat}'

    if accept is not None:
        txt += f'  {accept}'

    ax.text(0.02, 0.92, txt, transform=ax.transAxes)

def accept_label(h, ss, sid, direct, accept_df):
    label = "N"
    if ((h, ss, sid, direct) in accept_df.index and
            accept_df[h, ss, sid, direct]):
        label = "Y"
    return label


def traj_fig(dfe, height, sid, ss, direction=None, show_ema=False, **args):
    """Plot trajectories for a single session identified by subject id and
    stimulus speed
    """
    # convert timedeltas to seconds as float - matplotlib can't handle them properly
    dfe = dfe[(dfe.stimulus_speed == ss) & (dfe.id == sid)].copy()
    dfe['time'] = pd.to_numeric(dfe['time']) / 1000000000

    fsize = 12, 8
    fig, ax = plt.subplots(figsize=fsize)
    traj_plot(ax, dfe, sid, ss, direction=direction, show_ema=show_ema, **args)
    fig.tight_layout(h_pad=0.4, w_pad=0.4, rect=(0, 0, 1, 0.97))
    title = f'height {height} stimulus speed {ss}'
    fig.text(0.3, 0.97, title, fontsize='large')


def seg_col(direction, seg_id):
    seg_cols = plt.cm.winter(np.linspace(0, 1, 3))
    if direction == 'N':
        seg_col = 'silver'
    elif seg_id == -1:
        seg_col = 'black'
    else:
        seg_col = seg_cols[seg_id % 3]
    return seg_col


def traj_col(traj_id):
    traj_cols = plt.cm.hsv(np.linspace(0, 1, 9))
    traj_col = traj_cols[traj_id % 9]
    return traj_col

