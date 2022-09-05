import matplotlib
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import NullFormatter

from figs.utils import create_figure
from simulator.expt.actual import get_actual_summ
from simulator.sessrun.persist import retrieve_data


def iv2plot(ax, df, plotspec, linespecs=None, label_map=None, legend_map=None, grid=False, **_kwargs):
    """Line plots for multiple variables.

    Draw line plots of yvar against xvar for each value of linevar found in the data.
    Error bars are shown if the standard error for yvar is present in the data
    """

    if label_map is None:
        label_map = {}

    if legend_map is None:
        legend_map = {}

    xvar = plotspec['xvar']
    yvar = plotspec['yvar']
    linevar = plotspec['lvar']

    for lnum, (lval, ldf) in enumerate(df.groupby(linevar, sort=False)):
        lineattrs = linespecs[lnum] if linespecs else {}
        legend_label = legend_map.get(lval, lval)
        err_col = yvar + '_sem'
        if err_col in ldf.columns:
            ax.errorbar(ldf[xvar], ldf[yvar], yerr=ldf[err_col], fmt='-o',
                        label=legend_label, **lineattrs)
        else:
            ax.plot(ldf[xvar], ldf[yvar], label=legend_label, marker='.', **lineattrs)

    ax.set_ylabel(label_map.get(yvar, yvar), labelpad=1)
    ax.grid(grid)
    ax.set_xlabel(label_map.get(xvar, xvar))


def expt_plot(ax, df, xvar, yvar, lvar, xticks,  label_map, labels=None, xscale=None, colours=None, **kwargs):
    """Plot dataset df as a family of curves
    xvar - column containing values for x axis
    yvar - column containing values for y axis
    lvar - column specifying variable for each line
    """
    plotspec = {'xvar': xvar, 'yvar': yvar, 'lvar': lvar}

    if colours is None:
        colours = 'C0', 'C1', 'C2'

    ls1 = [ {'color': colour} for colour in colours]

        # ls1 = [
        #     {'color': 'C0'},
        #     {'color': 'C1'},
        #     {'color': 'C2'},
        # ]
        #


    iv2plot(ax, df=df, plotspec=plotspec, linespecs=ls1, label_map=label_map, **kwargs)

    if xscale is None:
        xscale = 'linear'
    ax.set_xscale(xscale)
    ax.set_xticks(xticks, labels)
    ax.get_xaxis().set_tick_params(which='minor', size=0)
    ax.get_xaxis().set_tick_params(which='minor', width=0)
    ax.get_xaxis().set_minor_formatter(NullFormatter())

    # ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

    # experiment!
    # ax.set_box_aspect(1.2)
    # ax.grid(False)


def expt_fig_spatial(path, fig_name=None, colours=None, xlim_map=None, ylim_map=None,
                     xscale=None, xticks=None, labels=None, **kwargs):
    """Draw figure for response to spatial frequency and height
    """
    print(f'generating {fig_name}')

    default_label_map = {
        'swim_speed': 'swim speed (mm/s)',
        'stimulus_speed': 'stimulus speed (mm/s)',
        'optic_flow': 'flow (rad/s)',
        'position': 'pos (mm)',
        'bout_rate': 'bout rate (Hz)',
        'bout_init_speed': 'bout initial speed (mm/s)',
        'baseline_speed': 'baseline stimulus speed (mm/s)',
        'omr_ratio': 'OMR ratio',
        'baseline_flow': 'baseline flow (rad/s)',
        'bout_active_duration': 'bout duration (s)',
        'spatial_frequency': 'spatial frequency (cpd)',
        'optomotor_index': 'optomotor index',
    }

    default_xlim_map = {
        'stimulus_speed': (3, 13),
        'baseline_flow': (0.05, 0.55),
    }

    default_ylim_map = {
        'swim_speed': (2, 23),
        'omr_ratio': (0, 2.5),
        'optomotor_index': (0, 0.7),
        'bout_rate': (1.25, 2.7),
        'bout_init_speed': (0, 60),
    }

    # labels for different height levels
    legend_map = {'h1': 'low', 'h4': 'medium', 'h7': 'high'}


    fig, ax = create_figure(1, 1, fig_name=fig_name, **kwargs)

    # for proc, expt_axs in zip(procs, axs):
    #     # load the experimental data appropriate for the procedure
    #     actual_summ = get_actual_summ(proc, full=True)
    #     if proc == 'BF':
    #         indep_var = 'baseline_flow'
    #         xticks = [0.1, 0.2, 0.3, 0.4, 0.5]
    #
    #     elif proc == 'OR':
    #         indep_var = 'stimulus_speed'
    #         xticks = [4, 6, 8, 10, 12]
    #
    #     else:
    #         raise ValueError('procedure must be BF or OR')



    # path = '../data/expt/other/spatial2.csv'
    # df = retrieve_data(path)

    dept_var = 'optomotor_index'

    df = pd.read_csv(path)

    if xticks is None:
        xticks = [0.01, 0.015, 0.02]

    # ax.set_xscale('log')

    expt_plot(ax, df, xvar='spatial_frequency', lvar='height_category', yvar=dept_var, colours=colours,
              xscale=xscale, xticks=xticks, labels=labels, label_map=default_label_map, legend_map=legend_map, **kwargs)

    # set x limits
    # if xlim_map is None:
    #     xlim_map = {}
    # xlim_map = {**default_xlim_map, **xlim_map}
    # if indep_var in xlim_map:
    #     xmin, xmax = xlim_map[indep_var]
    #     ax.set_xlim(xmin, xmax)
    #
    # set y limits
    if ylim_map is None:
        ylim_map = {}
    ylim_map = {**default_ylim_map, **ylim_map}
    if dept_var in ylim_map:
        ymin, ymax = ylim_map[dept_var]
        ax.set_ylim(ymin, ymax)

    # show legend for the top-left plot only
    # axs[0][0].legend(loc='lower left', bbox_to_anchor=(0.04, 0.63), frameon=False)
    # axs[0][0].legend(loc='lower left', bbox_to_anchor=(0.04, 0.63), frameon=False, title='Height')
    ax.legend(loc='upper left', frameon=False, title='Height')


    return fig



def test():
    dept_vars = ['bout_active_duration']
    fig_name = ''
    path = '../data/expt/other/spatial2.csv'
    fig = expt_fig_spatial(path=path, fig_name=fig_name)


if __name__ == "__main__":
    test()
    plt.show()
