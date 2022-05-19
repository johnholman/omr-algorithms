# calculate mean square error between actual and predicted values
import math
import time
from concurrent import futures
from datetime import datetime
from functools import lru_cache
from itertools import product, repeat

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_numeric_dtype

from simulator.expt.actual import get_actual_summ
from simulator.sessrun.cache import ResultsCache
from simulator.sessrun.erunner import run_expt
from simulator.sessrun.util import load_data, save_data, import_obj, get_expt_cfg


def grid_search(grid_spec, cfg, vcfg, description, actual_summ, derived_parms=None, max_workers=8, save=True,
                columns=None):
    grid_values = list(product(*grid_spec.values()))
    nruns = len(grid_values)
    grid_vars = grid_spec.keys()
    if derived_parms is None:
        derived_parms = {}
    start = time.time()

    startstr = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    print(
        f'search {nruns} combinations started at {startstr} with {max_workers} workers')
    cfgs = []
    grid_bindings = []
    model_bindings = []
    for n, vals in enumerate(grid_values):
        # grid_binding = {'n': n}
        grid_binding = {}
        model_binding = {'n': n}
        for var, val in zip(grid_vars, vals):
            grid_binding[var] = val
            # grid variables with names ending in _grid are not model parameters
            if not var.endswith('_grid'):
                model_binding[var] = val

        # add derived model parameters for this grid point by applying rules to the grid variables
        for parm, rule in derived_parms.items():
            model_binding[parm] = eval(rule, None, grid_binding)

        grid_bindings.append(grid_binding)
        model_bindings.append(model_binding)

        # add combination of parameters to the configuration
        cfg = {**cfg, **model_binding}
        cfgs.append(cfg)

    # import the model-specific comparison function given in configuration
    common_cfg = get_expt_cfg(cfg, vcfg)['common']
    comp_fn = import_obj('comparison_summary_fn', **common_cfg)

    with futures.ProcessPoolExecutor(max_workers=max_workers) as pool:
        results = pool.map(fit, repeat(description), cfgs, repeat(vcfg), repeat(actual_summ), grid_bindings,
                           repeat(comp_fn), repeat(columns))

    # merge and save the varied model parameters and corresponding errors for each fitting run
    # results = [{**rec, **err} for rec, err in zip(grid_bindings, errors)]
    # fit_df = pd.DataFrame(results)

    grid_df = pd.DataFrame(grid_bindings)
    # add '_grid' to the users grid variable names before saving
    grid_df.columns = [var if var.endswith('_grid') else var + '_grid' for var in grid_vars]
    fit_df = pd.concat((pd.DataFrame(model_bindings), grid_df, pd.DataFrame(results)), axis=1)

    if save:
        fname = 'fit' + datetime.now().strftime("_%Y-%m-%d_%H%M-%S")
        save_data(fit_df, filename='fit', format='csv')
        save_data(fit_df, filename=fname, format='csv')

    print(f'search finished at {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    duration = time.time() - start
    print(f'duration {int(duration)}s')

    return fit_df


def compare_point(point, **kwargs):
    names = tuple(point.keys())
    values = tuple(point.values())
    results = compare_points(grid_vars=names, grid_values=[values], **kwargs)
    result = dict(results.iloc[0])
    return result


def cost_with_gradient(*, point, grad_steps, **cost_args):
    gpoints = grad_points_fd(point, grad_steps)
    results = cost_points([point, *gpoints], **cost_args)
    cost, *grad_costs = results['cost']
    print(f'cost {cost} costs of displaced points {grad_costs}')
    cost_grad = grad_fd(y=cost, grad_y=grad_costs, steps=grad_steps)
    return cost, cost_grad, results


def grad_points_fd(point, grad_steps):
    d = len(point)
    points = []
    for i in range(d):
        grad_point = list(point)
        grad_point[i] += grad_steps[i]
        points.append(tuple(grad_point))
    return points


def grad_fd(y, grad_y, steps):
    grad = tuple((y1 - y) / step for y1, step in zip(grad_y, steps))
    return grad


def cost_points(values, features, **kwargs):
    errs_df = compare_points(grid_values=values, **kwargs)
    costs_df = cost_errors(errs_df, features=features)
    # costs = tuple(costs_df.cost)
    # results = { 'costs': costs, 'all': costs_df}
    return costs_df


def compare_grid(grid_spec, cfg, vcfg, description, actual_summ, **kwargs):
    """Return prediction errors when comparing predictions made by the model for a grid of search space parameters
    with the true values
    """
    grid_values = list(product(*grid_spec.values()))
    grid_vars = tuple(grid_spec.keys())
    results = compare_points(grid_vars=grid_vars, grid_values=grid_values, cfg=cfg, vcfg=vcfg, description=description,
                             actual_summ=actual_summ, **kwargs)
    return results


def compare_points(*, grid_vars, grid_values, cfg, vcfg, description, actual_summ, derived_parms=None, max_workers=8,
                   save=True,
                   columns=None, expt_name=None, project_name=None,
                   verbose=True):
    nruns = len(grid_values)
    if derived_parms is None:
        derived_parms = {}
    start = time.time()

    startstr = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    if verbose:
        print(
            f'evaluation of {nruns} combinations started at {startstr} with {max_workers} workers')

    # load  previous results from the result cache, if any
    cache = ResultsCache(grid_vars, project_name=project_name, expt_name=expt_name)
    cache_found = cache.load()
    if verbose:
        if cache_found:
            print(f'{len(cache)} cached results found')
        else:
            print(f'cached results not found')

    cfgs = []
    grid_bindings = []
    model_bindings = []
    new_grid_bindings = []
    old_results = []
    for n, vals in enumerate(grid_values):
        # grid_binding = {'n': n}
        grid_binding = {}
        model_binding = {'n': n}
        for var, val in zip(grid_vars, vals):
            grid_binding[var] = val
            # grid variables with names ending in _grid are not model parameters
            if not var.endswith('_grid'):
                model_binding[var] = val

        # add derived model parameters for this grid point by applying rules to the grid variables
        for parm, rule in derived_parms.items():
            model_binding[parm] = eval(rule, None, grid_binding)

        grid_bindings.append(grid_binding)
        model_bindings.append(model_binding)

        # create lists of grid bindings and configurations to be evaluated
        if grid_binding in cache:
            result = cache[grid_binding]
            old_results.append(result)
        else:
            new_grid_bindings.append(grid_binding)
            # add combination of parameters to the configuration
            cfg = {**cfg, **model_binding}
            cfgs.append(cfg)

    if verbose:
        print(f'evaluating {len(new_grid_bindings)} new parameter combinations')
    # import the model-specific comparison function given in configuration
    common_cfg = get_expt_cfg(cfg, vcfg)['common']
    comp_fn = import_obj('comparison_summary_fn', **common_cfg)

    with futures.ProcessPoolExecutor(max_workers=max_workers) as pool:
        new_results = pool.map(fit, repeat(description), cfgs, repeat(vcfg), repeat(actual_summ), new_grid_bindings,
                               repeat(comp_fn), repeat(columns))

    # add new results to the cache and compile all the results into a dataframe.
    for gv, result in zip(new_grid_bindings, new_results):
        cache[gv] = result
    cache.save()
    results = [cache[gv] for gv in grid_bindings]

    grid_df = pd.DataFrame(grid_bindings)
    # add '_grid' to the users grid variable names before saving
    grid_df.columns = [var if var.endswith('_grid') else var + '_grid' for var in grid_vars]
    fit_df = pd.concat((pd.DataFrame(model_bindings), grid_df, pd.DataFrame(results)), axis=1)

    if save:
        fname = 'fit' + datetime.now().strftime("_%Y-%m-%d_%H%M-%S")
        save_data(fit_df, filename='fit', format='csv', project_name=project_name, expt_name=expt_name)
        save_data(fit_df, filename=fname, format='csv', project_name=project_name, expt_name=expt_name)

    if verbose:
        print(f'search finished at {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
        duration = time.time() - start
        print(f'duration {int(duration)}s')

    return fit_df


def fit(description, cfg, vcfg, actual_summ, grid_binding, comp_fn, columns):
    # generate synthetic data for the given parameters
    try:
        md, df = run_expt(description=description, cfg=cfg, vcfg=vcfg, save=False, verbose=False)
    except OverflowError as err:
        print(f'{cfg["n"]} error {err}\ncfg:\n{cfg}\nvcfg:{vcfg}')
        return {}

    # use the function provided to summarise the last 20s of generated data
    predicted_summ = comp_fn(df, period=-20)

    # calculate number of conditions and number of valid conditions
    num_conditions = len(predicted_summ)
    num_valid_conditions = predicted_summ.is_valid.sum()

    # compare actual and generated data on the given columns to find prediction errors for these parameters
    results = compare_data(actual_summ, predicted_summ, columns=columns, md=md)
    results['num_conditions_np'] = num_conditions
    results['num_valid_conditions_np'] = num_valid_conditions

    print(f'{cfg["n"]} params: {grid_binding} results: {results}')

    return results


def optimal_fit(features, *, cost_df=None, filename='fit', expt_name=None, project_name=None, cost='cost', n=None):
    """ Return fitted parameters, grid variables and errors with the lowest value in the given cost column

        Grid variable names are translated from saved format to user format by removing the _grid suffix
        if the grid variable is also a model parameter
    """
    if cost_df is None:
        cost_df = costed_results(features=tuple(features), filename=filename, expt_name=expt_name,
                                 project_name=project_name)

    # consider

    if n is None:
        candidates = cost_df[cost_df.is_valid_np]
        result = candidates.loc[candidates[cost].idxmin()]
        n = candidates[cost].idxmin()
    else:
        result = cost_df.loc[n]

    # split result Series into a nested dict for different kinds of info
    cost = None
    parms = {}
    search_vars = {}
    abs_errs = {}
    rel_errs = {}

    for var, val in result.items():
        if var == 'cost':
            cost = val
        elif var.endswith('_err'):
            abs_errs[var] = val
        elif var.endswith('_grid'):
            search_vars[var] = val
        elif var.endswith('_norm'):
            rel_errs[var] = val
        elif var == 'poptimal' or var == 'n' or var.endswith('_np'):
            pass
        else:
            parms[var] = val

    if len(search_vars) == 0:
        # old format results assume grid variables and varied model parameters are the same
        user_search_vars = parms
    else:
        # remove the '_grid' suffix from grid variables that are also model parameters
        user_search_vars = {}
        for var, val in search_vars.items():
            stem = var[:-len('_grid')]
            if stem in parms:
                user_search_vars[stem] = val
            else:
                user_search_vars[var] = val

    result = {'parms': parms, 'search_vars': user_search_vars, 'abs_errs': abs_errs, 'rel_errs': rel_errs,
              'cost': cost, 'result_id': n}

    return result


def best_fit(*args, **kwargs):
    result = optimal_fit(*args, **kwargs)

    return result['parms'], result['abs_errs']


def fitted_parameters(*args, **kwargs):
    result = optimal_fit(*args, **kwargs)
    return result['parms']


def fitting_results(filename='fit', expt_name=None, project_name=None):
    return load_data(filename=filename, expt_name=expt_name, project_name=project_name)


@lru_cache(maxsize=None)
def costed_results(*, features, filename='fit', expt_name=None, project_name=None):
    """Return fitting results costed on the given tuple of features

    The fitting results are retrieved from persistent store
    Features must be given as a tuple as cannot be cached if not hashable
    """
    fit_df = load_data(filename=filename, expt_name=expt_name, project_name=project_name)
    cost_df = cost_errors(fit_df, features=features)
    return cost_df


@lru_cache
def get_means():
    # expt_dir = get_expt_dir()
    # # actual_summ_path_bf = r'~\data\ezfish\analysis\exp9_bf\group_summ'
    # actual_summ_path_bf = os.path.join(expt_dir, 'bf/group_summ')
    # actual_summ_bf = retrieve_data(actual_summ_path_bf)
    # bfdf = actual_summ_bf[actual_summ_bf.stimulus_speed >= 1.0]
    #
    # # actual_summ_path_or = r'~\data\ezfish\analysis\exp10_omr\group_summ'
    # actual_summ_path_or = os.path.join(expt_dir, 'or/group_summ')
    # ordf = retrieve_data(actual_summ_path_or)
    # alldf = pd.concat((ordf, bfdf)).reset_index(drop=True)

    alldf = get_actual_summ()
    means = alldf[['bout_rate', 'bout_init_speed', 'swim_speed', 'omr_ratio']].mean()
    # means = alldf.mean()[['bout_rate', 'bout_init_speed', 'swim_speed', 'omr_ratio']]
    print(means)
    return means


def cost_errors(fit_df, *, features):
    """Cost results on one or more features

    Calculates relative error scores for bout rate, initial speed and mean swim speed, and takes the mean of the
    relative errors for the costed features to determine the cost. Input results must include absolute error scores
    for the costed features.
    """
    # filter out any row with missing values
    # TODO: redundancy here, left over from previous implementation, but not harmful
    fit_df = fit_df[fit_df.notna().all(axis=1)]
    if 'num_conditions_np' in fit_df.columns:
        # mark as invalid results based on more than 2 invalid conditions, if that info is available
        # fit_df = fit_df.assign(is_valid_np=fit_df.num_conditions_np - fit_df.num_valid_conditions_np <= 2)
        fit_df = fit_df.assign(is_valid_np=True)
    else:
        # mark any result with missing data as invalid
        fit_df = fit_df.assign(is_valid_np=fit_df.notna().all(axis=1))

    # calculate the relative errors
    err_df = rel_errors(fit_df)

    # costs are the means of relative errors for the given features
    cost = err_df[[feature + '_err_norm' for feature in features]].mean(axis=1)
    cost_df = err_df.assign(cost=cost)

    return cost_df


def rel_errors(fit_df):
    """Return dataframe with relative errors added for all features where the mean is available

    The absolute errors are divided by the overall observed means for the corresponding feature.
    """
    means = get_means()
    relerrs = {}
    for feature, mean in means.items():
        feature_err = feature + '_err'
        if feature_err in fit_df:
            relerrs[feature_err + '_norm'] = fit_df[feature_err] / mean
    err_df = fit_df.assign(**relerrs)
    return err_df


def pareto_optimal(costs):
    """Return boolean list indicating which rows are Pareto optimal

    A row is Pareto optimal if there is no other row with no higher cost feature
    and at least one lower cost feature
    """
    optimal = [True] * len(costs)
    for c1 in costs.values:
        for i, c2 in enumerate(costs.values):
            if np.all(c1 <= c2) and np.any(c1 < c2):
                optimal[i] = False
    return optimal


def compare_data(actual, predicted, md=None, columns=None, join_vars=None):
    assert md is not None or (columns is not None and join_vars is not None)

    if columns is None:
        columns = md.get('comparison_vars')

    if join_vars is None:
        join_vars = md.get('join_vars')

    if len(actual) != len(predicted):
        raise ValueError(f'{len(actual)} actual records but {len(predicted)} predicted records')

    # sort data in order of independent variables
    left = actual.sort_values(by=join_vars).reset_index()
    right = predicted.sort_values(by=join_vars).reset_index()

    # check that independent vars have same values within fp error
    for iv in join_vars:
        liv = left[iv]
        riv = right[iv]
        if not (liv.equals(riv) or (is_numeric_dtype(liv) and is_numeric_dtype(riv) and np.all(np.isclose(liv, riv)))):
            print(liv, riv)
            raise ValueError(f"values of independent variable {iv} differs between actual and predicted data")

    merged = pd.merge(right, left, left_index=True, right_index=True)

    results = {col + '_err': math.sqrt(((merged[col + '_x'] - merged[col + '_y']) ** 2).mean()) for col in columns if
               col + '_x' in merged and col + '_y' in merged}

    return results


if __name__ == '__main__':
    pass
