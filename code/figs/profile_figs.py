import os

import pandas as pd
import matplotlib.pyplot as plt

from expts.bouts.profile import calc_profile
from figs.utils import create_figure
from simulator.expt.actual import get_actual_dir
from simulator.sessrun.persist import retrieve_data

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.float_format', '{:.5f}'.format)


def plot_profile(df, ax, **kwargs):
    """Plot the bout intensity profile for the given data
    """
    p = calc_profile(df)
    ax.plot(range(0, 1000, 10), p, **kwargs)
    ax.set_xlabel('time after bout start (ms)')
    ax.set_ylabel('relative speed', labelpad=1)
    ax.set_ylim(0, 7.5)


def plot_quartile_profiles(df, ax, column):
    """Plot intensity profiles for the given data using the given access.

    The data is partitioned based on the quartile values for the given column and the profile
    calculated and displayed for each partition
    """
    bouts = df.groupby(['source', 'id', 'height', 'stimulus_speed', 'direction', 'seg_id', 'bout_num'])

    values = bouts.first()[column]

    q1, q2, q3 = values.quantile(q=(0.25, 0.5, 0.75))

    print(f'{column} quantiles: {q1} {q2} {q3}')

    df1 = df[df[column] <= q1]
    p1 = calc_profile(df1)

    df2 = df[(df[column] > q1) & (df[column] <= q2)]
    p2 = calc_profile(df2)

    df3 = df[(df[column] > q2) & (df[column] <= q3)]
    p3 = calc_profile(df3)

    df4 = df[df[column] > q3]
    p4 = calc_profile(df4)

    ax.plot(range(0, 1000, 10), p1, label='first', color='black')
    ax.plot(range(0, 1000, 10), p2, label='second', color='cyan')
    ax.plot(range(0, 1000, 10), p3, label='third', color='purple')
    ax.plot(range(0, 1000, 10), p4, label='fourth', color='red')
    ax.legend(title='quartile', frameon=False)
    ax.set_xlabel('time after bout start (ms)')
    ax.set_ylabel('relative speed')
    ax.set_ylim(0, 7.5)


def overall_profile_fig(expt_dir=None, fig_name=None, **kwargs):
    print(f'generating {fig_name}')
    # calculate intensity profiles from the combined experimental data and show profile figures
    # infile = '~/data/ezfish/analysis/common/full.feather'
    if expt_dir is None:
        expt_dir = get_actual_dir('ALL')
    infile = os.path.join(expt_dir, 'bouts_ts')
    df = retrieve_data(infile)
    # include only timesteps in bouts
    df = df[df.bout_num != -1]

    fig, ax = create_figure(fig_name=fig_name, **kwargs)
    # fig, axs = create_figure(2, fig_name=fig_name, **kwargs)

    plot_profile(df, ax, label='all bouts', color='indigo')
    # ax.set_title('all bouts')

    plot_profile(df[df.omr_bout], ax, label='OMR bouts', color='orangered')

    ax.legend(frameon=False)

    return fig


def quartile_profile_fig(expt_dir=None, quartile_feature='bout_initial_speed', fig_name=None, **kwargs):
    print(f'generating {fig_name}')
    # calculate intensity profiles from the combined experimental data and show profile figures
    if expt_dir is None:
        expt_dir = get_actual_dir('ALL')
    infile = os.path.join(expt_dir, 'bouts_ts')
    df = retrieve_data(infile)

    # include only timesteps in bouts
    df = df[df.bout_num != -1]

    fig, ((ax1, ax2),) = create_figure(2, fig_name=fig_name, **kwargs)

    plot_quartile_profiles(df, ax1, quartile_feature)
    ax1.set_title('all bouts')

    plot_quartile_profiles(df[df.omr_bout], ax2, quartile_feature)
    ax2.set_title('OMR bouts')

    return fig


if __name__ == '__main__':
    overall_profile_fig(fig_name='bout profiles')
    plt.show()
    print('finished')
