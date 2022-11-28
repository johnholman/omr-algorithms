import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import stats

from figs.utils import create_figure


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


def expt_plot(ax, df, xvar, yvar, lvar, xticks, label_map, **kwargs):
    """Plot dataset df as a family of curves
    xvar - column containing values for x axis
    yvar - column containing values for y axis
    lvar - column specifying variable for each line
    """
    plotspec = {'xvar': xvar, 'yvar': yvar, 'lvar': lvar}
    ls1 = [
        {'color': 'C0'},
        {'color': 'C1'},
        {'color': 'C2'},
    ]

    iv2plot(ax, df=df, plotspec=plotspec, linespecs=ls1, label_map=label_map, **kwargs)

    ax.set_xticks(xticks)

    # experiment!
    # ax.set_box_aspect(1.2)
    # ax.grid(False)


def expt_correlation_fig(path, procs, dept_vars, fig_name=None, xlim_map=None, ylim_map=None, **kwargs):
    """Draw figure comparing observed and predicted statistics

    A plot is generated for each experiment and dependent variables showing observed and predicted values for
    each dependent variable

    :param procs: list of experimental procedures ("BF" for baseline flow, "OR" for OMR regulation)
    :param dept_vars: list of dependent variables to plot
    :param fig_name: filename for saving the figure (defaults to None)
    :param xlim_map: map from variable name to axis limits
    :param ylim_map: map from variable name to axis limits
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
        'omr_corr': "Pearson's R",
    }

    default_xlim_map = {
        'stimulus_speed': (3, 13),
        'baseline_flow': (0.05, 0.55),
    }

    default_ylim_map = {
        'swim_speed': (2, 23),
        'omr_ratio': (0.5, 2),
        'bout_rate': (1.25, 2.7),
        'bout_init_speed': (0, 60),
        'omr_corr': (-0.04, 0.35),
    }

    # labels for different height levels
    legend_map = {'h1': 'low', 'h4': 'medium', 'h7': 'high'}

    df = pd.read_csv(path)

    # for multiple experiments/procedures, layout is one row per experiment
    # nv = len(dept_vars)
    # np = len(procs)
    # if nv > np:
    #     fig, axs = create_figure(nv*np, nrows=np, fig_name=fig_name, **kwargs)
    # else:
    #     fig, axs = create_figure(nv*np, nrows=nv, fig_name=fig_name, **kwargs)

    fig, ax = create_figure(len(procs) * len(dept_vars), nrows=len(procs), fig_name=fig_name, **kwargs)

    for proc in procs:
        # load the experimental data appropriate for the procedure
        # actual_summ = get_actual_summ(proc, full=True)
        if proc == 'BF':
            indep_var = 'baseline_flow'
            xticks = [0.1, 0.2, 0.3, 0.4, 0.5]
            bdf = df[df.source == 'BF']
        elif proc == 'OR':
            indep_var = 'stimulus_speed'
            xticks = [4, 6, 8, 10, 12]
            bdf = df[df.source == 'OR']

        else:
            raise ValueError('procedure must be BF or OR')

        # generate plot for each dependent variable
        for dept_var in dept_vars:
            expt_plot(ax, bdf, xvar=indep_var, lvar='height_category', yvar=dept_var,
                      xticks=xticks, label_map=default_label_map, legend_map=legend_map, **kwargs)

            # set x limits
            if xlim_map is None:
                xlim_map = {}
            xlim_map = {**default_xlim_map, **xlim_map}
            if indep_var in xlim_map:
                xmin, xmax = xlim_map[indep_var]
                ax.set_xlim(xmin, xmax)

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
    ax.axhline(0, color='black', linestyle='dotted')

    return fig

def scatter():
    bouts_file = "../data/expt/all/bouts_summ.feather"
    bdf = pd.read_feather(bouts_file)
    proc = 'OR'
    ss = 8.0
    ht = 'h4'
    # gdf = bdf[(bdf.source == proc) & (bdf.stimulus_speed == ss) & (bdf.height_category == ht) & bdf.omr_bout]
    gdf = bdf[(bdf.source == proc) & (bdf.stimulus_speed == ss) & (bdf.height_category == ht)]

    corr = gdf.bout_initial_speed.corr(gdf.bout_duration)
    print(f'correlation: {corr}')

    res = stats.linregress(gdf.bout_initial_speed, gdf.bout_duration)
    print(f'intercept {res.intercept}  slope {res.slope}  R {res.rvalue} p {res.pvalue} SEM of slope {res.stderr}')

    sdx = gdf.bout_initial_speed.std()
    sdy = gdf.bout_duration.std()
    slope = res.rvalue * sdy / sdx

    print(f'sd bout initial speed {gdf.bout_initial_speed.std()} duration {gdf.bout_duration.std()} slope {slope}')

    fig, ax = plt.subplots()
    ax.scatter(gdf.bout_initial_speed, gdf.bout_duration)
    ax.set_xlim(0, 80)
    ax.set_ylim(0.2, 0.9)

    xvals = np.array(ax.get_xlim())
    yvals = res.intercept + res.slope * xvals
    ax.plot(xvals, yvals, color='red')


    return gdf




if __name__ == "__main__":
    scatter()
    plt.show()
