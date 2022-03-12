from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

from figs.utils import create_figure
from simulator.expt.actual import get_actual_summ
from simulator.sessrun.util import load_data


def compare_fig(expts, procs, dep_vars, proj_name=None,
                vars_in_cols=True, fig_name=None, xlim_map=None, ylim_map=None, **kwargs):
    """Draw figure comparing observed and predicted statistics

    A plot is generated for each experiment and dependent variables showing observed and predicted values for
    each dependent variable

    :param expts: list of simulation experiments
    :param procs: list of corresponding procedures ("BF" for baseline flow, "OR" for OMR regulation)
    :param dep_vars: list of dependent variables to plot
    :param proj_name: project name (defaults to "pub21")
    :param vars_in_cols: whether subplots for dependent variables for the same procedure are presented in a column
    :param xlim_map: map from variable name to axis limits
    :param ylim_map: map from variable name to axis limits
    :param fig_name: filename for saving the figure (defaults to None)
    """
    print(f'generating {fig_name}')

    default_label_map = {
        'start_rate': 'Poisson rate (Hz)',
        'swim_speed': 'swim speed (mm/s)',
        'ground_speed': 'SOG (ground_speed) (mm/s)',
        'stimulus_speed': 'stimulus speed (mm/s)',
        'integral_error': 'ierr',
        'integrated_flow': 'integrated flow',
        'motor_output': 'motor output',
        'optic_flow': 'flow (rad/s)',
        'sensed_flow': 'sensed flow\n(rad/s)',
        'f_rate': 'flow facilitation',
        'm_rate': 'motor inhibition',
        'intensity_flow': 'weighted\nintensity flow',
        'intensity_scale': 'intensity scale',
        'scaled_impulse': 'scaled impulse',
        'position': 'pos (mm)',
        'bout_rate': 'bout rate (Hz)',
        'bout_init_speed': 'bout initial speed (mm/s)',
        'smoothed_optic_flow': 'smoothed optic flow (rad/s)',
        'smoothed_motor_drive': 'smoothed motor drive',
        'smoothed_ground_speed': 'smoothed SOG (mm/s)',
        'smoothed_swim_speed': 'smoothed swim speed (mm/s)',
        'smoothed_stimulus_speed': 'smoothed stimulus speed (mm/s)',
        'smoothed_omr_ratio': 'smoothed OMR ratio',
        'baseline_speed': 'baseline stimulus speed (mm/s)',
        'ssbf_ratio': 'swim speed to baseline flow ratio',
        'omr_ratio': 'OMR ratio',
        'swim_speed_req': 'swim speed to hold position (mm/s)',
        'baseline_flow': 'baseline flow (rad/s)'
    }

    default_xlim_map = {
        'stimulus_speed': (3, 13),
        'baseline_flow': (0.05, 0.55),
    }

    if vars_in_cols:
        default_ylim_map = {
            'swim_speed': (2, 24),
            'omr_ratio': (0.5, 2),
            'bout_rate': (1.25, 3.0),
            'bout_init_speed': (0, 50),
        }
    else:
        default_ylim_map = {
            'swim_speed': (2, 28),
            'omr_ratio': (0.5, 2),
            'bout_rate': (1.25, 2.8),
            'bout_init_speed': (5, 60),
        }

    if vars_in_cols:
        nrows = len(dep_vars)
        ncols = len(procs)
    else:
        nrows = len(procs)
        ncols = len(dep_vars)

    fig, axs = create_figure(nrows * ncols, nrows=nrows, fig_name=fig_name, **kwargs)

    if vars_in_cols:
        axs = axs.T

    for (nexpt, (expt, proc, expt_axs)) in enumerate(zip(expts, procs, axs)):
        # load the experimental data appropriate for the procedure
        actual_summ = get_actual_summ(proc)
        if proc == 'BF':
            indep_var = 'baseline_flow'
            title = "Baseline flow experiment"
            xticks = [0.1, 0.2, 0.3, 0.4, 0.5]
        elif proc == 'OR':
            indep_var = 'stimulus_speed'
            title = "OMR regulation experiment"
            xticks = [4, 6, 8, 10, 12]
        else:
            raise ValueError('procedure must be BF or OR')

        # load the synthetic data for the experiment and add height_category column
        predicted_summ = load_data('group_summary', expt_name=expt, project_name=proj_name)
        height_category = predicted_summ['height'].map({8.0: 'h1', 32.0: 'h4', 56.0: 'h7'})
        predicted_summ = predicted_summ.assign(height_category=height_category)

        # generate plot for each dependent variable
        for (nvar, (ax, dept_var)) in enumerate(zip(expt_axs, dep_vars)):
            compare_plot(ax, actual_summ, predicted_summ, xvar=indep_var, lvar='height_category', yvar=dept_var,
                         xticks=xticks, label_map=default_label_map, **kwargs)

            if len(dep_vars) == 1 and nexpt > 0:
                hide_ticks_labels(ax, 'y')

            # always hide all but bottom x axis decorations (special case but good enough here)
            if nvar != nrows - 1 and vars_in_cols:
                hide_ticks_labels(ax, 'x')

            if len(procs) > 1:
                ax.set_title(title)

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
    show_legend(axs[0][0])

    return fig


def hide_ticks_labels(ax, which):
    if which == 'y':
        ax.tick_params(
            axis='y',  # changes apply to the y-axis
            which='both',  # both major and minor ticks are affected
            left=False,  # ticks along the bottom edge are off
            labelleft=False)  # tick labels along the bottom edge are off
        ax.set_ylabel(None)
    elif which == 'x':
        ax.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            labelbottom=False)  # tick labels along the bottom edge are off
        ax.set_xlabel(None)
    else:
        raise ValueError()


def compare_plot(ax, df1, df2, xvar, yvar, lvar, xticks, **kwargs):
    """Plot two datasets df1, df2 on the same axes as families of curves
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
    ls2 = [
        {'color': 'C0', 'linestyle': 'dashed'},
        {'color': 'C1', 'linestyle': 'dashed'},
        {'color': 'C2', 'linestyle': 'dashed'},
    ]
    iv2plot(ax, df=df1, plotspec=plotspec, linespecs=ls1, **kwargs)
    iv2plot(ax, df=df2, plotspec=plotspec, linespecs=ls2, **kwargs)
    ax.set_xticks(xticks)


def show_legend(ax):
    lines = ax.get_lines()

    blank = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)

    handles = [blank, blank, blank, blank,
               blank, lines[0], lines[1], lines[2],
               blank, lines[3], lines[4], lines[5]
               ]
    labels = ['', 'low', 'med', 'high',
              'actual', '', '', '',
              'predicted', '', '', '']

    ax.legend(handles, labels, ncol=3, handletextpad=-3.7, borderpad=0, frameon=False,
              loc='upper left', bbox_to_anchor=(0.12, 0.98))

    # ax.legend(handles, labels, ncol=3, handletextpad=-3.7, borderpad=0, frameon=False,
    #           loc='lower left', bbox_to_anchor=(0.12, 0.66))
    #


def show_legend_old(ax):
    lines = ax.get_lines()

    blank = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)

    handles = [blank, blank, blank, blank,
               blank, lines[0], lines[1], lines[2],
               blank, lines[3], lines[4], lines[5]
               ]
    labels = ['', 'low', 'medium', 'high',
              'observed', '', '', '',
              'predicted', '', '', '']

    ax.legend(handles, labels, ncol=3, handletextpad=-2.5, borderpad=1)


def iv2plot(ax, df, plotspec, linespecs=None, label_map=None, grid=False, **_kwargs):
    """Line plots for multiple variables.

    Draw line plots of yvar against xvar for each value of linevar found in the data.
    Error bars are shown if the standard error for yvar is present in the data
    """

    if label_map is None:
        label_map = {}

    xvar = plotspec['xvar']
    yvar = plotspec['yvar']
    linevar = plotspec['lvar']

    for lnum, (lval, ldf) in enumerate(df.groupby(linevar, sort=False)):
        lineattrs = linespecs[lnum] if linespecs else {}
        err_col = yvar + '_sem'
        if err_col in ldf.columns:
            ax.errorbar(ldf[xvar], ldf[yvar], yerr=ldf[err_col], fmt='-o',
                        **lineattrs)
        else:
            ax.plot(ldf[xvar], ldf[yvar], marker='.', **lineattrs)

    ax.set_ylabel(label_map.get(yvar, yvar))
    ax.grid(grid)
    ax.set_xlabel(label_map.get(xvar, xvar))


# def compare_fig1(expts, procs, dept_vars, proj_name='pub21', fig_name=None, xlim_map=None, ylim_map=None, **kwargs):
#     """Draw figure comparing observed and predicted statistics
#
#     A plot is generated for each experiment and dependent variables showing observed and predicted values for
#     each dependent variable
#
#     :param expts: list of simulation experiments
#     :param procs: list of corresponding procedures ("BF" for baseline flow, "OR" for OMR regulation)
#     :param dept_vars: list of dependent variables to plot
#     :param proj_name: project name (defaults to "pub21")
#     :param fig_name: filename for saving the figure (defaults to None)
#     """
#     print(f'generating {fig_name}')
#
#     default_label_map = {
#         'start_rate': 'Poisson rate (Hz)',
#         'swim_speed': 'swim speed (mm/s)',
#         'ground_speed': 'SOG (ground_speed) (mm/s)',
#         'stimulus_speed': 'stimulus speed (mm/s)',
#         'integral_error': 'ierr',
#         'integrated_flow': 'integrated flow',
#         'motor_output': 'motor output',
#         'optic_flow': 'flow (rad/s)',
#         'sensed_flow': 'sensed flow\n(rad/s)',
#         'f_rate': 'flow facilitation',
#         'm_rate': 'motor inhibition',
#         'intensity_flow': 'weighted\nintensity flow',
#         'intensity_scale': 'intensity scale',
#         'scaled_impulse': 'scaled impulse',
#         'position': 'pos (mm)',
#         'bout_rate': 'bout rate (Hz)',
#         'bout_init_speed': 'bout initial speed (mm/s)',
#         'smoothed_optic_flow': 'smoothed optic flow (rad/s)',
#         'smoothed_motor_drive': 'smoothed motor drive',
#         'smoothed_ground_speed': 'smoothed SOG (mm/s)',
#         'smoothed_swim_speed': 'smoothed swim speed (mm/s)',
#         'smoothed_stimulus_speed': 'smoothed stimulus speed (mm/s)',
#         'smoothed_omr_ratio': 'smoothed OMR ratio',
#         'baseline_speed': 'baseline stimulus speed (mm/s)',
#         'ssbf_ratio': 'swim speed to baseline flow ratio',
#         'omr_ratio': 'OMR ratio',
#         'swim_speed_req': 'swim speed to hold position (mm/s)',
#         'baseline_flow': 'baseline flow (rad/s)'
#     }
#
#     default_xlim_map = {
#         'stimulus_speed': (3, 13),
#         'baseline_flow': (0.05, 0.55),
#     }
#
#     default_ylim_map = {
#         'swim_speed': (2, 28),
#         'omr_ratio': (0.5, 2),
#         'bout_rate': (1.25, 2.5),
#         'bout_init_speed': (0, 60),
#     }
#
#     # if len(procs) > 1:
#     #     # for multiple experiments/procedures, layout is one row per experiment
#     #     fig, axs = create_figure(len(procs) * len(dept_vars), ncolumns=len(dept_vars), fig_name=fig_name, **kwargs)
#     # else:
#     #     # if just showing a single experiment, layout dep vars in two columns
#     #     fig, axs = create_figure(len(procs) * len(dept_vars), ncolumns=2, fig_name=fig_name, **kwargs)
#     #     # and then reshape the array of axes to have one row per experiment
#     #     axs = axs.reshape([1, -1])
#
#     fig, axs = create_figure(len(procs) * len(dept_vars), nrows=len(procs), fig_name=fig_name, **kwargs)
#
#     for expt, proc, expt_axs in zip(expts, procs, axs):
#         # load the experimental data appropriate for the procedure
#         if proc == 'BF':
#             actual_summ_path = r'~\data\ezfish\analysis\exp9_bf\group_summ'
#             actual_summ = retrieve_data(actual_summ_path)
#             actual_summ = actual_summ[actual_summ.stimulus_speed >= 1.0]
#             indep_var = 'baseline_flow'
#             title = "Baseline flow experiment"
#             xticks = [0.1, 0.2, 0.3, 0.4, 0.5]
#         elif proc == 'OR':
#             actual_summ_path = r'~\data\ezfish\analysis\exp10_omr\group_summ'
#             actual_summ = retrieve_data(actual_summ_path)
#             indep_var = 'stimulus_speed'
#             title = "OMR regulation experiment"
#             xticks = [4, 6, 8, 10, 12]
#         else:
#             raise ValueError('procedure must be BF or OR')
#
#         # expt_axs[0].set_title(title, loc='left')
#
#         # load the synthetic data for the experiment and add height_category column
#         predicted_summ = load_data('group_summary', expt_name=expt, project_name=proj_name)
#         height_category = predicted_summ['height'].map({8.0: 'h1', 32.0: 'h4', 56.0: 'h7'})
#         predicted_summ = predicted_summ.assign(height_category=height_category)
#
#         # generate plot for each dependent variable
#         for ax, dept_var in zip(expt_axs, dept_vars):
#             compare_plot(ax, actual_summ, predicted_summ, xvar=indep_var, lvar='height_category', yvar=dept_var,
#                          xticks=xticks, label_map=default_label_map, **kwargs)
#
#             # set x limits
#             if xlim_map is None:
#                 xlim_map = {}
#             xlim_map = {**default_xlim_map, **xlim_map}
#             if indep_var in xlim_map:
#                 xmin, xmax = xlim_map[indep_var]
#                 ax.set_xlim(xmin, xmax)
#
#             # set y limits
#             if ylim_map is None:
#                 ylim_map = {}
#             ylim_map = {**default_ylim_map, **ylim_map}
#             if dept_var in ylim_map:
#                 ymin, ymax = ylim_map[dept_var]
#                 ax.set_ylim(ymin, ymax)
#
#             #
#             # if dept_var in ylim_map:
#             #     ymin, ymax = ylim_map[dept_var]
#             #     ax.set_ylim(ymin, ymax)
#
#     # show legend for the top-left plot only
#     show_legend(axs[0][0])
#
#     # fig.suptitle(title)
#
#     return fig


def test():
    expts = ['li_single_o_sbo', 'li_single_b_sbo']
    dept_vars = ['swim_speed', 'omr_ratio']
    fig_name = '3.3 simple model fitted to swim speed'
    compare_fig(expts=expts, procs=['OR', 'BF'], dep_vars=dept_vars, fig_name=fig_name)

    expts = ['pmi_fli_b_ribo']
    dept_vars = ['bout_rate', 'bout_init_speed']
    fig_name = 'x.x final model BF performance'
    compare_fig(expts=expts, procs=['BF'], dep_vars=dept_vars, fig_name=fig_name, vsize=5)

    expts = ['pmi_fli_o_ribo', 'pmi_fli_b_ribo']
    dept_vars = ['bout_rate', 'bout_init_speed', 'swim_speed', 'omr_ratio']
    compare_fig(expts=expts, procs=['OR', 'BF'], dep_vars=dept_vars, proj_name='pub21orig'
                                                                               '')


if __name__ == "__main__":
    test()
    plt.show()
