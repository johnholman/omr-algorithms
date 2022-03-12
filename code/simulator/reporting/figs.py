# from analysis.report import report_indiv, report_groups
import math
import os
from itertools import product
from numbers import Real

import matplotlib.pyplot as plt
from matplotlib import gridspec

from simulator.sessrun.util import get_data_folders


def select_period(df, period):
    """ Return data after selecting rows for the given time period

    Examples:
          select_period(df, 5) - select data for first 5 s
          select_period(df, -2) - select data for last 2 s
          select_period(df, (5, 10)) - select data for period 5 s- 10 s
    """
    start_time = 0
    end_time = None
    if isinstance(period, Real):
        if float(period) > 0.0:  # think requirement for this cast might be PyCharm bug
            end_time = period
        else:
            start_time = df.time.max() + period
    elif isinstance(period, tuple):
        start_time, end_time = period

    # select only timesteps for required period
    if end_time is None:
        df = df[df.time > start_time]
    else:
        df = df[(df.time >= start_time) & (df.time <= end_time)]

    return df


def label_period(period):
    """ Return descriptive label for a period

    Examples:
          select_period(df, 5) -> "session for first 5s"
          select_period(df, -2) -> "session for last 2s"
          select_period(df, (5, 10)) -> "session from 5s to 10s"
    """
    if isinstance(period, Real):
        if float(period) > 0.0:  # think requirement for this cast might be PyCharm bug
            label = f'session for first {period}s'
        else:
            label = f'session for last {-period}s'
    elif isinstance(period, tuple):
        start_time, end_time = period
        label = f'session from {start_time}s to {end_time}s'
    elif period is None:
        label = 'full session'
    else:
        raise ValueError(f'invalid period specification {period}')

    return label


def groups_summ_fig(data, *, plotspecs, title=None, hsize=None, vsize=None,
                    linespecs=None, label_map=None, fig=None, axes=None, ncolumns=1, **_args):
    if label_map is None:
        label_map = {}

    md = None
    if isinstance(data, tuple):
        md, df = data
    else:
        df = data

    nplots = len(plotspecs)

    if title is None:
        title = 'group summary figure'

    if fig is None or axes is None:
        fig, axes = create_figure(nplots=nplots, ncolumns=ncolumns, hsize=hsize, vsize=vsize, title=title)

    mplglobal = {'fontsize': 20, 'labelsize': 18, 'linewidth': 3}

    if linespecs is None:
        linespecs, *_ = default_linespecs(md)

    if isinstance(linespecs, dict):
        linespecs = expand_linespec(linespecs)
    #     print(f'linespecs {linespecs}')

    if md is not None:
        label_map = {**label_map, **md.get('default_label_map')}

    for plot_num, plotspec in enumerate(plotspecs):
        plotspec = {**mplglobal, **plotspec}
        if 'lvar' in plotspec:
            iv2plot(ax=axes[plot_num], df=df, plotspec=plotspec, linespecs=linespecs, label_map=label_map)
        else:
            lineattrs = linespecs[0] if linespecs else {}
            iv1plot(ax=axes[plot_num], df=df, plotspec=plotspec, lineattrs=lineattrs, label_map=label_map)

    fig.tight_layout(h_pad=0)

    return fig, axes


def create_figure(nplots, ncolumns=1, hsize=None, vsize=None, title=None):
    """Return figure and list of axes
    """
    nrows = math.ceil(nplots / ncolumns)

    # print(f'{nrows=} {ncolumns=}')

    # calculate defaults for figure size
    if vsize is None:
        if nrows == 1:
            vsize = 6
        elif nrows == 2:
            vsize = 8
        else:
            vsize = 10
    if hsize is None:
        if ncolumns == 1:
            hsize = 9
        elif ncolumns == 2:
            hsize = 12
        else:
            hsize = 15

    _, project, expt_name = get_data_folders()

    # fignum = f'{project}:{expt}' if title is None else f'{title} ({project}:{expt})'

    fignum = f'{expt_name} {next_fignum()} - {title}' if title else f'{expt_name} {next_fignum()}'
    fig, axes = plt.subplots(nrows, ncolumns, figsize=(hsize, vsize), num=fignum, squeeze=False)
    # gs = gridspec.GridSpec(nrows, ncolumns)
    axes = axes.flatten()

    return fig, axes


def next_fignum():
    next_fignum.num += 1
    return next_fignum.num


next_fignum.num = 0


def save_figure(fig, figdir, format='pdf'):
    fname = fig.get_label() + '.' + format
    figpath = os.path.join(figdir, fname)
    figpath = os.path.normpath(os.path.expanduser(figpath))

    fig.savefig(figpath, format=format)


def iv1plot(ax, df, plotspec, lineattrs=None, label_map=None):
    """Line plot for a single independent variable."""

    if label_map is None:
        label_map = {}
    if lineattrs is None:
        lineattrs = {}

    xvar = plotspec['xvar']
    yvar = plotspec['yvar']

    err_col = yvar + '_sem'
    if err_col in df.columns:
        ax.errorbar(df[xvar], df[yvar], yerr=df[err_col], fmt='-o', **lineattrs)
    else:
        ax.plot(df[xvar], df[yvar], marker='.', **lineattrs)

    ax.set_ylabel(label_map.get(yvar, yvar))
    ax.set_xlabel(label_map.get(xvar, xvar))

    ax.grid(True)


def iv2plot(ax, df, plotspec, linespecs=None, label_map=None):
    """Line plots for multiple variables.
    
    Draw line plots of yvar against xvar for each value of linevar found in the data.
    Error bars are shown if the standard error for yvar is present in the data 
    """

    if label_map is None:
        label_map = {}

    xvar = plotspec['xvar']
    yvar = plotspec['yvar']
    linevar = plotspec['lvar']
    linevar_label = label_map.get(linevar, linevar)
    title = plotspec.get('title')

    for lnum, (lval, ldf) in enumerate(df.groupby(linevar, sort=False)):
        lineattrs = linespecs[lnum] if linespecs else {}
        v = f'{lval:.3f}' if isinstance(lval, float) else f'{lval}'
        err_col = yvar + '_sem'
        if err_col in ldf.columns:
            ax.errorbar(ldf[xvar], ldf[yvar], yerr=ldf[err_col], fmt='-o',
                        label=f'{linevar_label}={v}', **lineattrs)
        else:
            ax.plot(ldf[xvar], ldf[yvar],
                    #                     label=f'{linevar_label}={lval :.3f}', marker='.', **lineattrs)
                    label=f'{linevar_label}={v}', marker='.', **lineattrs)

        ax.legend()
        ax.set_ylabel(label_map.get(yvar, yvar))
        ax.grid(True)
        ax.set_xlabel(label_map.get(xvar, xvar))
        if title:
            ax.title(title)


def groups_traj_fig(data, *, title=None, plot_indep_vars=None,
                    dep_vars=None, linespec=None, hsize=None, vsize=None,
                    ymarg=None, linespecs=None, linespecs2=None,
                    label_map=None, **args):
    if label_map is None:
        label_map = {}

    md, df = data
    # take means over subjects
    df = df.groupby(['group_id', 'phase_id', 'step_num'], sort=False).mean()

    data = md, df

    _indep_vars, dep_vars = default_vars(rpt_type='groups_traj', data=data, dep_vars=dep_vars)
    var_names = plot_indep_vars + dep_vars if plot_indep_vars else dep_vars
    print(f'Variables for groups trajectory plot: {var_names}\n')

    nplots = len(var_names)
    #     print(f'{nplots} axes {var_names}')

    # set default figure dimensions if not specified by the user 
    if hsize is None:
        hsize = 9
    if vsize is None:
        if nplots == 1:
            vsize = 6
        elif nplots == 2:
            vsize = 8
        else:
            vsize = 10

    if linespec is None and linespecs is None:
        linespecs, linespecs2 = default_linespecs(md)

    # set up line specifications either from the old "linespec" attribute or new "primary_linespecs" and
    # "secondary_linespecs"
    expanded_linespecs = []
    if linespec:  # old syntax linespec - dictionary with entry for each group
        #         groups = md['config']['']['groups']
        groups = md.get('groups')
        expanded_linespecs = []
        for group_id in groups:
            linestyle, color = linespec.get(group_id)
            spec = {'linestyle': linestyle, 'color': color}
            expanded_linespecs.append(spec)

    elif linespecs:  # new syntax

        # expand abbreviated dict format into a list of lineattrs
        if isinstance(linespecs, dict):
            linespecs = expand_linespec(linespecs)

        # if secondary specifications present then take the cartesian product to generate the lineattrs list
        if linespecs2:
            if isinstance(linespecs2, dict):
                linespecs2 = expand_linespec(linespecs2)

            # combine relevant elements in the two lists to define each line
            expanded_linespecs = [{**pair[0], **pair[1]} for pair in product(linespecs, linespecs2)]

        else:
            expanded_linespecs = linespecs

    #     print(f'linespecs {expanded_linespecs}')

    label_map = {**label_map, **md.get('default_label_map')}

    fig = plt.figure(num=title, figsize=(hsize, vsize))
    gs = gridspec.GridSpec(len(var_names), 1)

    # add default entries to label map

    # set up axes for all subplots 
    for axis_num, var_name in enumerate(var_names):
        ax = fig.add_subplot(gs[axis_num, 0])

        plot_info = {'var_name': var_name}

        # show x axis labels etc for bottom plot only
        if var_name != var_names[-1]:
            plot_info['full_x'] = False

        if var_name != var_names[0]:
            plot_info['legend'] = False

        if ymarg is not None:
            plot_info['ymarg'] = ymarg

        groups_traj_plot(ax=ax, data=data, plot_info=plot_info, linespecs=expanded_linespecs, label_map=label_map,
                         **args)

    fig.tight_layout(h_pad=0)


def expand_linespec(spec):
    lspecs = []
    for name, values in spec.items():
        lspecs.append([{name: value} for value in values])
    spec1 = []
    for dicts in zip(*lspecs):
        merged_dicts = {}
        for d in dicts:
            merged_dicts = {**merged_dicts, **d}
        spec1.append(merged_dicts)
    return spec1


def groups_traj_plot(*, ax, data, plot_info, linespecs=None, label_map=None, **args):
    if label_map is None:
        label_map = {}

    md, df = data

    # take means over subjects - this will be done in advance probably
    df = df.groupby(['group_id', 'phase_id', 'step_num'], sort=False).mean()

    #     print(f'groups_traj_plot - plotinfo {plot_info}\nlinespecs {linespecs}')

    plot_info = plot_info.copy()  # to avoid mutating arguments
    var_name = plot_info.pop('var_name')

    # labels for the legend
    labels = md.default_labels(label_map)

    fontsize = plot_info.pop('fontsize', None)
    y_label = plot_info.pop('y_label', label_map.get(var_name, var_name))
    ax.set_ylabel(y_label, fontsize=fontsize)

    if plot_info.pop('full_x', True):
        ax.set_xlabel('time (s)', fontsize=fontsize)
        ax.tick_params(axis='both', which='major', labelsize=plot_info.pop('labelsize', None))
    else:
        ax.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        ax.tick_params(axis='y', which='major', labelsize=plot_info.pop('labelsize', None))

    ax.margins(y=plot_info.pop('ymarg', None))
    y_lim = plot_info.pop('y_lim', None)
    if y_lim is not None:
        ax.set_ylim(y_lim)

    ax.grid()

    # plot each group
    grouped = df.groupby(['group_id'])
    if linespecs and len(grouped) > len(linespecs):
        raise ValueError(f'{len(grouped)} groups but only {len(linespecs)} line attribute specifications')
    for gnum, (group_id, group_df) in enumerate(grouped):
        lineattrs = linespecs[gnum] if linespecs else {}

        # # adjust times to be relative to start of selected phases for each group
        # group_df = group_df.copy()  # otherwise get a warning bout writing to a view
        # group_df['time'] -= group_df['time'].iloc[0]

        # add smoothed variant of a variable if name beings with "smoothed_"
        group_df = group_df.copy()  # we're about to add variables in place ..
        if var_name.startswith('smoothed_'):
            add_smoothed_var(var_name, group_df, **args)

        ax.plot(group_df['time'], group_df[var_name], label=labels[group_id], **lineattrs)

    legend_fontsize = plot_info.pop('legend_fontsize', None)
    if plot_info.pop('legend', True):
        ax.legend(fontsize=legend_fontsize)

    # apply changes to the plots
    for key, value in plot_info.items():
        if key == 'linewidth':
            plt.setp(ax.lines, 'linewidth', value)
        else:
            print(f"unknown plot info key {key} with value {value}")


def indiv_traj_fig(data, *, title=None, group_id=None, plot_indep_vars=None,
                   dep_vars=None, ymarg=None, hsize=None, vsize=None,
                   label_map=None, lineattrs=None, save_fig=False, **args):
    md, df = data

    if label_map is None:
        label_map = {}
    label_map = {**label_map, **md.get('default_label_map')}

    _indep_vars, dep_vars = default_vars(rpt_type='indiv_traj', data=data, dep_vars=dep_vars)

    var_names = plot_indep_vars + dep_vars if plot_indep_vars else dep_vars
    #     print(f'Variables for individual trajectory plots: {var_names}')

    nplots = len(var_names)

    # set default figure dimensions if not specified by the user 
    if hsize is None:
        hsize = 9

    if vsize is None:
        if nplots == 1:
            vsize = 6
        elif nplots == 2:
            vsize = 8
        else:
            vsize = 10

    fig = plt.figure(num=title, figsize=(hsize, vsize))
    gs = gridspec.GridSpec(nplots, 1)

    # s = ' '.join([ f'{label_map.get(var, var)}: {val}' for var, val in md.group(group_id).items()])
    fig.suptitle(md.group_label(group_id, label_map))

    axes = {}
    for axis_num, var_name in enumerate(var_names):
        axes[var_name] = ax = fig.add_subplot(gs[axis_num, 0])
        plot_info = {'ymarg': ymarg}

        # show x axis labels etc for bottom plot only
        if var_name == var_names[-1]:
            plot_info['full_x'] = True

        indiv_traj_plot(ax=ax, df=df, var_name=var_name, plot_info=plot_info,
                        lineattrs=lineattrs, label_map=label_map, **args)

    fig.tight_layout(h_pad=0)

    if save_fig:
        fig_path = md.get('fig_path')
        save_figure(fig, fig_path)


def indiv_traj_plot(*, ax, df, var_name, plot_info, lineattrs=None, label_map=None, **args):
    # y_label=None,  ymarg=None, ylim=None,
    #                     color=None, linestyle=None, linewidth=None, fontsize=None,
    #                     labelsize=None, **_args):

    if lineattrs is None:
        lineattrs = {}
    if label_map is None:
        label_map = {}

    # add smoothed variant of the variable if name beings with "smoothed_"
    if var_name.startswith('smoothed_'):
        add_smoothed_var(var_name, df, **args)

    y_label = label_map.get(var_name, var_name)

    fontsize = plot_info.get('fontsize')
    ax.set_ylabel(y_label, fontsize=fontsize)
    ymarg = plot_info.get('ymarg')
    ax.margins(y=ymarg)
    ylim = plot_info.get('ylim')
    if ylim is not None:
        ax.set_ylim(ylim)
    labelsize = plot_info.get('labelsize')
    ax.tick_params(axis='both', which='major', labelsize=labelsize)

    if plot_info.get('full_x'):
        ax.set_xlabel('time (s)')
    else:
        ax.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        ax.set_xlabel(None)

    ax.plot(df['time'], df[var_name], **lineattrs)
    ax.grid()

    for key, value in plot_info.items():
        if key == 'linewidth':
            plt.setp(ax.lines, 'linewidth', value)


def add_smoothed_var(var_name, df, win_size=100, **_args):
    """ Return dataframe with added column of smooth values with the given variable name.

        First part of the variable name must be 'smoothed_' and rest the name of an existing
        column in the given dataframe.

        Smoothing is done by taking mean of rolling window of 100 points
    """
    first, *rest = var_name.split('_', 1)
    if first == 'smoothed' and len(rest) == 1 and rest[0] in df.columns:
        df[var_name] = df[rest[0]].rolling(window=win_size, center=True).mean()
    else:
        raise ValueError(f'basename for {var_name} not present as data column')
    return df


def default_vars(*, rpt_type, data, indep_vars=None, dep_vars=None):
    """ Return independent and dependent variables for given report type

    Defaults are supplied for the independent and dependent variables if not supplied
    The metadata is consulted for list of possible default and those present in the data are retained
    """

    def remove_prefix(text, prefix):
        return text[len(prefix):] if text.startswith(prefix) else text

    md, df = data
    iv = list(md.get('indep_vars').keys())
    dv = []
    for var in md.get(rpt_type + '_dep_vars'):
        basevar = remove_prefix(var, 'smoothed_')
        if basevar not in iv and basevar in df.columns:
            dv.append(var)

    if indep_vars is None:
        indep_vars = iv
    if dep_vars is None:
        dep_vars = dv
    # print(f"default_vars for {rpt_type}: {indep_vars=} {dep_vars=}")

    return indep_vars, dep_vars


def default_linespecs(md):
    """ Return default primary and secondary linespecs based on metadata

    Returns empty directories when these cannot be determined (e.g. experiment with differences between phases only)
    """
    linespecs = {}
    linespecs2 = {}
    colours = md.get('default_colours')
    styles = md.get('default_styles')
    ivar_spec = md.get('indep_vars')
    levels = [len(val) for val in ivar_spec.values()]
    if len(levels) > 0:
        n = levels[0]
        c = (colours * (n // len(colours) + 1))[:n]  # extend/truncate colours by recyling to required length
        linespecs = {'color': c}

    if len(levels) > 1:
        n = levels[1]
        s = (styles * (n // len(styles) + 1))[:n]  # extend/truncate styles by recyling to required length
        linespecs2 = {'linestyle': s}

    return linespecs, linespecs2


def compare_fig(actual, predicted, *, md, indep_vars, dep_vars, title=None, label_map=None, save_fig=False, **kwargs):
    """Generate figure comparing actual and predicted data"""
    lvar, xvar = indep_vars

    plotspecs = [{'xvar': xvar, 'yvar': yvar, 'lvar': lvar} for yvar in dep_vars]

    # create figure and axes common to the actual and predicted plots
    if title is None:
        title = 'comparison figure'

    fig, axes = create_figure(len(dep_vars), title=title, **kwargs)

    if label_map is None:
        label_map = {}
    label_map = {**md.get('default_label_map'), **label_map}
    vlabel = label_map[lvar] if label_map is not None else lvar

    # summary figure for the experimental data
    linespecs = {'color': ['C0', 'C1', 'C2']}
    label_map[lvar] = f'actual: {vlabel}'
    groups_summ_fig(actual, fignum=title, plotspecs=plotspecs, linespecs=linespecs,
                    label_map=label_map, fig=fig, axes=axes, **kwargs)

    # summary figure for the simulation data
    linespecs = {'color': ['C0', 'C1', 'C2'], 'linestyle': ['dashed'] * 3}
    label_map[lvar] = f'predicted: {vlabel}'
    groups_summ_fig(predicted, plotspecs=plotspecs, linespecs=linespecs, label_map=label_map,
                    fig=fig, axes=axes, **kwargs)

    if save_fig:
        fig_path = md.get('fig_path')
        save_figure(fig, fig_path)
