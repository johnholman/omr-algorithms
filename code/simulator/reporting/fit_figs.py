import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, tri

from simulator.sessrun.fit import optimal_fit, costed_results


def fit_fig(*, fit_df, features, report_vars, opt_grid_vars, islog, zval=None):
    fig, axs = plt.subplots(ncols=3, figsize=(15, 5), constrained_layout=True)
    fig.set_constrained_layout_pads(w_pad=4 / 72, h_pad=4 / 72, hspace=0, wspace=0)

    xvar = report_vars[0]
    xscale = islog[0]
    yvar = report_vars[1]
    yscale = islog[1]
    zvar = report_vars[2] if len(report_vars) >= 3 else None

    triangles = tri.Triangulation(fit_df[xvar], fit_df[yvar])
    if zvar is not None:
        fig.suptitle(f'{zvar} = {zval}')

    errs = [feature + '_err' for feature in features]

    if 'cost' in fit_df:
        errs += ['cost']

    for n, (ax, err) in enumerate(zip(axs, errs)):

        ax.set_xlabel(xvar)

        if n == 0:
            ax.set_ylabel(yvar)

        if xscale:
            ax.set_xscale('log')

        if yscale:
            ax.set_yscale('log')

        cs = ax.tricontourf(triangles, fit_df[err], levels=256, extend='both')
        cs1 = ax.tricontour(triangles, fit_df[err], levels=8, colors='grey', )

        ax.clabel(cs1, inline=1, fontsize=10)

        ax.scatter(fit_df[xvar], fit_df[yvar], marker='o', color='black')

        if 'is_valid' in fit_df:
            ax.scatter(fit_df.loc[~fit_df.is_valid, xvar], fit_df.loc[~fit_df.is_valid, yvar], marker='o', color='red')

        # indicate position of optimum point
        ax.scatter(opt_grid_vars[xvar], opt_grid_vars[yvar], marker='o', color='white')

        fig.colorbar(cs, ax=ax, aspect=10, orientation='horizontal', format='%.1f')
        ax.set_title(err)

        # create ticks and tick labels for tested levels
        xtl = fit_df[xvar].unique()
        ax.set_xticks(xtl)
        ax.set_xticklabels([f'{s:.2f}' for s in xtl])
        ytl = fit_df[yvar].unique()
        ax.set_yticks(ytl)
        ax.set_yticklabels([f'{s:.2f}' for s in ytl])
        ax.minorticks_off()


def contour_fit_figs(*, costed_features, expt_name=None, project_name=None, display_features=None, report_vars=None):
    """ Generate figures showing error contour plots based on fitting results

    :param costed_features: features considered to determine the best combination of grid variables
    in the fitting results.
    :param expt_name: experiment name for the fitting results (defaults to current script name)
    :param project_name: project name for the fitting results (defaults to current package name)
    :param display_features: features to show error contours for (defaults to the costed features)
    :param report_vars: grid variables to report errors for (defaults to the three with most levels)

    The first report variable is plotted on the x axis, second on the y axis. Either of these may be suffixed
    with ":log" to use log rather linear scaling. If a third variable is given then a separate figure is generated
    for each of its levels. Values of all variables listed as report variables are fixed at the values found for
    the best fit.
    """
    if display_features is None:
        display_features = costed_features

    fit_df = costed_results(expt_name=expt_name, project_name=project_name, features=tuple(costed_features))
    # parms, opt_grid_vars, errs = optimal_fit(costed_features, cost_df=fit_df)
    result = optimal_fit(costed_features, cost_df=fit_df)
    opt_grid_vars = result['search_vars']
    errs = result['abs_errs']

    # choose up to three variables to report preferring those with the most levels
    if report_vars is None:
        # get number of levels for each grid variables
        levels = {v: len(fit_df[v].unique()) for v in opt_grid_vars}

        # choose the three variables with most levels to be the reported ones by default
        report_vars = [k for k, v in sorted(levels.items(), key=lambda item: item[1], reverse=True)][:3]

    # parse out scale specifiers
    rvars = []
    islog = []
    for spec in report_vars:
        parts = spec.split(':')
        rvars.append(parts[0])
        islog.append(len(parts) == 2 and parts[1] == 'log')

    # check that primary report variables have enough levels.
    if len(fit_df[rvars[0]].unique()) < 3 or len(fit_df[rvars[1]].unique()) < 3:
        print(f'Too few levels for variables {rvars[:2]} to generate error contours')
        return

    criteria = {var: val for var, val in opt_grid_vars.items() if var not in rvars}

    print(f'best grid vars {opt_grid_vars}')
    print(f'report variables {report_vars}')
    print(f'selection criteria {criteria}')

    # select rows with optimal values for any unreported variables
    if len(criteria) > 0:
        mask = pd.DataFrame([fit_df[key] == val for key, val in criteria.items()]).all()
        fit_df = fit_df[mask]

    # clip display features and cost to increase resolution for the regions of interest
    err_features = [var + '_err' for var in display_features if var != 'cost']
    err_features.append('cost')
    m = 3
    fit_df = fit_df.copy()
    for var, val in errs.items():
        if var in err_features:
            fit_df[var] = np.clip(fit_df[var], 0, val * m)

    if len(rvars) <= 2:
        fit_fig(fit_df=fit_df, features=display_features, report_vars=rvars, opt_grid_vars=opt_grid_vars, islog=islog)
    else:
        for val, df in fit_df.groupby([rvars[2]]):
            fit_fig(fit_df=df, features=display_features, report_vars=rvars, opt_grid_vars=opt_grid_vars, islog=islog,
                    zval=val)


if __name__ == '__main__':
    def test():
        # features = 'bout_rate', 'bout_init_speed'
        features = ['swim_speed']
        display_features = ['bout_rate', 'bout_init_speed', 'swim_speed']
        report_vars = ['Ke:log', 'ki_tau_prod_grid:log']
        project_name = 'single'
        ename = 'wo_lid_rpprof_s_fit'
        contour_fit_figs(expt_name=ename, project_name=project_name, costed_features=features,
                         display_features=display_features, report_vars=report_vars)
        report_vars = ['ki_tau_prod_grid:log', 'start_bias', 'Ke:log']
        contour_fit_figs(expt_name=ename, project_name=project_name, costed_features=features,
                         display_features=display_features, report_vars=report_vars)

        report_vars = ['ki_tau_prod_grid:log', 'start_bias']
        display_features = ['swim_speed']
        contour_fit_figs(expt_name=ename, project_name=project_name, costed_features=features,
                         display_features=display_features, report_vars=report_vars)


    test()
    plt.show()
