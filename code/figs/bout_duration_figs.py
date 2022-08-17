import os

import pandas as pd
from matplotlib import pyplot as plt

from figs.utils import create_figure
from simulator.expt.actual import get_actual_dir
from simulator.sessrun.persist import retrieve_data

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.float_format', '{:.5f}'.format)


def bout_duration_fig(expt_dir=None, fig_name=None, **kwargs):
    fig, ax = create_figure(1, fig_name=fig_name, **kwargs)

    if expt_dir is None:
        expt_dir = get_actual_dir('ALL')
    boutsf = os.path.join(expt_dir, 'bouts_summ')
    allbouts = retrieve_data(boutsf)
    # boutsf = '~/data/ezfish/analysis/common/bouts.feather'
    # allbouts = load_data(boutsf)

    nbouts = len(allbouts)
    less250 = (len(allbouts.bout_duration[allbouts.bout_duration < 0.25]) / nbouts) * 100
    less200 = (len(allbouts.bout_duration[allbouts.bout_duration < 0.2]) / nbouts) * 100

    print(f"percentage bouts with duration < 200ms {less200} < 250ms {less250}")

    omrbouts = allbouts[allbouts.omr_bout]

    ax.hist(omrbouts.bout_duration[omrbouts.bout_duration < 1]*1000, bins=20)
    ax.set_ylabel('number of bouts')
    ax.set_xlabel('time to next bout (ms)')
    ax.axvline(250, color='red')
    # ax.set_xticks(range(0, 1000, 200))
    return fig


def bout_duration_multi_fig(expt_dir, fig_name=None, **kwargs):
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = create_figure(9, nrows=3, fig_name=fig_name, **kwargs)

    if expt_dir is None:
        expt_dir = get_actual_dir('ALL')
    boutsf = os.path.join(expt_dir, 'bouts')
    allbouts = retrieve_data(boutsf)

    # boutsf = '~/data/ezfish/analysis/common/bouts.feather'
    # allbouts = load_data(boutsf)

    nbouts = len(allbouts)

    less250 = (len(allbouts.bout_duration[allbouts.bout_duration < 0.25]) / nbouts) * 100
    less200 = (len(allbouts.bout_duration[allbouts.bout_duration < 0.2]) / nbouts) * 100

    print(f"percentage bouts with duration < 200ms {less200} < 250ms {less250}")

    omrbouts = allbouts[allbouts.omr_bout]

    otherbouts = allbouts[~allbouts.omr_bout]

    # fig, axes = plt.subplots(3, 3, figsize=(15, 12))

    # (ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9) = axs

    ax1.hist(allbouts.bout_initial_speed, bins=40)
    ax1.set_title('bout initial speeds')

    ax2.hist(allbouts.bout_initial_speed[allbouts.bout_initial_speed < 20], bins=10)
    ax2.set_title('bout initial speeds up to 20 mm/s')

    ax4.hist(allbouts.bout_duration, bins=40)
    ax4.set_title('bout duration - all bouts')

    ax5.hist(allbouts.bout_duration[allbouts.bout_duration < 0.5], bins=20)
    ax5.set_title('bout duration up to 500ms - all bouts')

    ax6.hist(omrbouts.bout_duration[omrbouts.bout_duration < 0.5], bins=20)
    ax6.set_title('bout duration up to 500ms - omr bouts only')

    ax7.hist(otherbouts.bout_duration, bins=40)
    ax7.set_title('bout duration - non-omr bouts')

    ax8.hist(otherbouts.bout_duration[otherbouts.bout_duration < 0.5], bins=20)
    ax8.set_title('bout duration up to 500ms - non-omr bouts')

    return fig


if __name__ == '__main__':
    bout_duration_fig('bout histo', size=(150, 150))
    plt.show()
