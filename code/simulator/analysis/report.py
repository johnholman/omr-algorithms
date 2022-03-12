from math import isclose

import numpy as np

from simulator.analysis.summary import summarise_groups, add_derived_variables, indiv_analysis, \
    summarise_groups_for_comparison
from simulator.reporting.figs import default_vars, label_period, groups_summ_fig, \
    select_period, indiv_traj_fig, groups_traj_fig, next_fignum
from simulator.reporting.report import compare_rpt, set_pandas_options
from simulator.sessrun.fit import costed_results, optimal_fit
from simulator.sessrun.util import get_data, save_data


def indiv_rpt_expt(dref=None, *, title=None, groups=None, **args):
    """
    Generate individual level reports

    :param dref: data to report upon
    :param title: title for report
    :param groups: group ids to generate report for (default: all groups)
    :param title: text to add to report title
    """
    md, df = data = get_data(dref)

    set_pandas_options()
    print(df.head(3))
    print(f'number of records: {len(df)}')

    # generate reports for all groups by default
    if groups is None:
        groups = md.get('groups')
    else:
        groups = [str(group_id) for group_id in groups]

    # groups = md.get('groups')
    name = md.get('name')
    print(f'report for {name}\n  dref columns {list(df.columns)}')
    for group_id in groups:
        group_id = str(group_id)  # force to a string
        suffix = f'indiv for group {group_id}'
        fignum = next_fignum()
        fulltitle = f'{name} {fignum} {title} - {suffix}' if title else f'{name} {fignum} - {suffix}'
        report_indiv(data, title=fulltitle, group_id=group_id, **args)


def report_indiv(dref=None, *, group_id="1", subj_id=1, period=None, bout_stats=False, **args):
    md, df = get_data(dref)

    # extract records for required individual
    df = df[(df['group_id'] == group_id) & (df['subj_id'] == subj_id)].copy()

    # extract for required period
    df = select_period(df, period)

    df = add_derived_variables(df)

    data = md, df

    if bout_stats:
        indiv_analysis(data, group_id=group_id, subj_id=subj_id, **args)
    indiv_traj_fig(data, group_id=group_id, subj_id=subj_id, **args)


def group_rpt_expt(dref=None, *, phase_spec=None, title=None, **args):
    md, _df = data = get_data(dref)

    name = md.get('name')

    if phase_spec is None:
        fignum = next_fignum()
        suffix = f'group trajectories ({name})'
        title = f'{fignum} {title} - {suffix}' if title else f'{fignum} {suffix}'
        report_group_trajectories(data, title=title, **args)
    else:
        for phases in phase_spec:
            fignum = next_fignum()
            fulltitle = f'{fignum} {title} -' if title else f'{fignum} '
            fulltitle += f'{" and ".join(phases)} ({name})'
            report_group_trajectories(data, title=fulltitle, phases=phases, **args)


def report_group_trajectories(dref=None, *, phases=None, period=None, **args):
    md, df = get_data(dref)

    # select required period and phases
    df = select_period(df, period)

    if phases is not None:
        df = df[df['phase_id'].isin(phases)]

    df = add_derived_variables(df)

    data = md, df
    groups_traj_fig(data, **args)


def summary_rpt_expt(dref=None, *, indep_vars=None, dep_vars=None, period=None, terminal_duration=None, **args):
    md, df = get_data(dref)

    # support terminal_duration parameter for backwards compatibility
    if terminal_duration is not None:
        period = -terminal_duration

    # analyse the data to get summary data
    summ_df = summarise_groups(df, period=period, **args)
    summary = md, summ_df
    save_data(summ_df.reset_index(), filename='group_summary', format='csv')

    # generate console report
    indep_vars, dep_vars = default_vars(rpt_type='summary', data=summary, indep_vars=indep_vars, dep_vars=dep_vars)

    print(f'Group summary report: indep vars {indep_vars} dep vars {dep_vars}\n')
    period_label = label_period(period)
    print(f'Summary for {period_label}')
    # calculate overall mean for the OMR ratio root mean square errors
    omr_rmse = summ_df['omr_rmse'].mean()
    print(f'\n{summ_df}\nOMR rmse {omr_rmse:.3f}\n')

    rpt_columns = ['group_id'] + indep_vars + dep_vars
    rpt = summ_df.reset_index().to_string(columns=rpt_columns, index=False, float_format=lambda x: "{:.3f}".format(x))
    print(rpt)

    # create plot specification for each subplot
    if len(indep_vars) == 2:
        lvar, xvar = indep_vars
        plotspecs = [{'xvar': xvar, 'yvar': yvar, 'lvar': lvar} for yvar in dep_vars]
    elif len(indep_vars) == 1:
        xvar = indep_vars[0]
        plotspecs = [{'xvar': xvar, 'yvar': yvar} for yvar in dep_vars]
    else:
        print(f'Cannot plot summaries for {len(indep_vars)} independent variables')
        return

    groups_summ_fig(summary, plotspecs=plotspecs, **args)


def report_comparison(*, predicted=None, indep_vars=None, dep_vars=None, actual_summ_path=None, actual_summ=None,
                      proc=None, **kwargs):
    """
    Generate report comparing actual and simulated data

    :param predicted: predicted data as dataframe
    :param indep_vars: independent variables
    :param dep_vars:  dependent variables
    :param actual_summ_path: file path to the actual data
    :param actual_summ: dataframe containing the actual data
    :param proc: procedure for which data was collected

    Any of the actual data, datapath, or procedure must be provided
    """

    if indep_vars is None:
        indep_vars = ['height_category', 'stimulus_speed']
    if dep_vars is None:
        dep_vars = ['swim_speed', 'ssbf_ratio', 'omr_ratio', 'bout_rate', 'bout_dist']
    label_map = {'height_category': 'height'}
    summ_fn = summarise_groups_for_comparison

    compare_rpt(predicted=predicted, summ_fn=summ_fn, indep_vars=indep_vars, dep_vars=dep_vars,
                actual_summ_path=actual_summ_path, actual_summ=actual_summ, proc=proc, label_map=label_map, **kwargs)


def report_fitting_results(*, features, cost_df=None, filename='fit', expt_name=None, project_name=None,
                           grid_spec=None, nbest=None, sort=True):
    """Report results of fitting"""
    # TODO clean up to separate cases where we have the costed results and when we don't
    if cost_df is None:
        cost_df = costed_results(features=tuple(features), filename=filename, expt_name=expt_name,
                                 project_name=project_name)
    if sort:
        cost_df = cost_df.sort_values(by=['cost', 'n'])

    # generate report for the required number of best candidates
    if nbest is not None:
        cost_df = cost_df.head(nbest)

    # console report for best n results
    print(rpt_results(cost_df, features))

    # console report for best fit
    if grid_spec is not None:
        result = optimal_fit(cost_df=cost_df, features=features)
        print(rep_best_result(grid_spec=grid_spec, features=features, result=result))


def rep_best_result(*, grid_spec, features, result):
    grid_vars = result['search_vars']
    parms = result['parms']
    abs_errs = result['abs_errs']
    rel_errs = result['rel_errs']
    cost = result['cost']

    pl = []
    for name in grid_spec.keys():
        best_val = grid_vars[name]
        values = grid_spec[name]
        vsl = []
        for val in values:
            s = f'{val:.8f}'
            if isclose(best_val, val):
                # if val == best_val:
                s = '*' + s
            vsl.append(s)
        valstr = name + ': [' + ', '.join(vsl) + ']'
        pl.append(valstr)
    gridstr = '\n'.join(pl)
    parmstr = ' '.join([f'{name}: {val:.3f}' for name, val in parms.items()])
    feature_errs = ['cost'] + [feature + '_err' for feature in features]
    errstr = ' '.join([f'{name}: {val:.3f}' for name, val in abs_errs.items() if name not in feature_errs])
    ferrstr = ' '.join([f'{name}: {val:.8f}' for name, val in abs_errs.items() if name in feature_errs])
    frelerrs = [feature + '_err_norm' for feature in features]  # relative error keys for features
    frelerrstr = ' '.join([f'{name}: {val:.8f}' for name, val in rel_errs.items() if name in frelerrs])
    coststr = f'{frelerrstr} cost: {cost: .8f}'

    return '\n' + gridstr + '\n' + parmstr + '\n' + errstr + '\n' + ferrstr + '\n' + coststr


def rpt_results(cost_df, features):
    """ Report fitting results in tabular format

    TODO: clean up what happens if features not provided
    """
    if features is None:
        features = []
    feature_str = f"costed by {', '.join(features)}"
    print(f"\nBest {len(cost_df)} fitting results {feature_str}")

    feature_errs = ['cost'] + [feature + '_err' for feature in features]

    # add columns to indicate Pareto optimality and cost, if multiple fitting objectives
    if 'poptimal' in cost_df:
        cost_df = cost_df.assign(po=np.where(cost_df['poptimal'], '*', ' '))
        rpt_cols = ['po'] + feature_errs + ['cost'] + list(cost_df.columns)
    else:
        rpt_cols = feature_errs + list(cost_df.columns)

    rpt_df = cost_df[rpt_cols]

    formatters = {'cost': '{:.8f}'.format}
    s = rpt_df.to_string(index=True, col_space=8, float_format=lambda x: "{:.5f}".format(x), formatters=formatters)
    return s
