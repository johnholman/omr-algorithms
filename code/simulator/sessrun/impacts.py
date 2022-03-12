import numpy as np

from simulator.sessrun.fit import costed_results


def gv_impact2(gs, results):
    tm = int((len(gs['tau']) - 1) / 2)
    km = int((len(gs['ke_tau_prod_grid']) - 1) / 2)
    srm = int((len(gs['sr_tau_prod_grid']) - 1) / 2)
    print(f'midpoints {tm} {km} {srm}')
    tl = (gs['tau'][0], gs['ke_tau_prod_grid'][km], gs['sr_tau_prod_grid'][srm])
    th = (gs['tau'][-1], gs['ke_tau_prod_grid'][km], gs['sr_tau_prod_grid'][srm])
    te = abs(results[th]['swim_speed_err'] - results[tl]['swim_speed_err'])
    kl = (gs['tau'][tm], gs['ke_tau_prod_grid'][0], gs['sr_tau_prod_grid'][srm])
    kh = (gs['tau'][tm], gs['ke_tau_prod_grid'][-1], gs['sr_tau_prod_grid'][srm])
    ke = abs(results[kh]['swim_speed_err'] - results[kl]['swim_speed_err'])
    srl = (gs['tau'][tm], gs['ke_tau_prod_grid'][km], gs['sr_tau_prod_grid'][0])
    srh = (gs['tau'][tm], gs['ke_tau_prod_grid'][km], gs['sr_tau_prod_grid'][-1])
    sre = abs(results[srh]['swim_speed_err'] - results[srl]['swim_speed_err'])

    return te, ke, sre


def gv_impact1(gs, results):
    tm = int((len(gs['tau']) - 1) / 2)
    km = int((len(gs['ke_tau_prod_grid']) - 1) / 2)
    srm = int((len(gs['sr_tau_prod_grid']) - 1) / 2)
    print(f'midpoints {tm} {km} {srm}')
    tl = (gs['tau'][0], gs['ke_tau_prod_grid'][km], gs['sr_tau_prod_grid'][srm])
    th = (gs['tau'][-1], gs['ke_tau_prod_grid'][km], gs['sr_tau_prod_grid'][srm])
    te = abs(results[th]['swim_speed_err'] - results[tl]['swim_speed_err'])
    kl = (gs['tau'][tm], gs['ke_tau_prod_grid'][0], gs['sr_tau_prod_grid'][srm])
    kh = (gs['tau'][tm], gs['ke_tau_prod_grid'][-1], gs['sr_tau_prod_grid'][srm])
    ke = abs(results[kh]['swim_speed_err'] - results[kl]['swim_speed_err'])
    srl = (gs['tau'][tm], gs['ke_tau_prod_grid'][km], gs['sr_tau_prod_grid'][0])
    srh = (gs['tau'][tm], gs['ke_tau_prod_grid'][km], gs['sr_tau_prod_grid'][-1])
    sre = abs(results[srh]['swim_speed_err'] - results[srl]['swim_speed_err'])

    return te, ke, sre


# def geom(n, r, c):
#     s = np.geomspace(c / r ** 0.5, c * r ** 0.5, num=n)
#     print(s)
#     return s
#
#
# grid_spec = {'tau': geom(3, 2, 0.05365392),
#              'ke_tau_prod_grid': geom(3, 2, 16.52397928),
#              'sr_tau_prod_grid': geom(3, 2, 33635.85661015),
#              }


def geom(n, r, c):
    s = list(np.geomspace(c / r ** 0.5, c * r ** 0.5, num=n))
    return s


def gv_impacts(dims, costs):
    """Return list of impacts of change in cost for each variable

    dims - list of number of values for each variable
    costs - linear list of costs associated with each binding of values to variables
    """
    nvars = len(dims)
    costs = np.array(costs)
    best_idx = costs.argmin()
    best_coords = np.unravel_index(best_idx, dims)
    min_cost = cost_by_coord(best_coords, costs, dims)

    impacts = [gv_impact(n, best_coords, costs, dims, min_cost) for n in range(nvars)]
    return impacts


# TODO this assumes every grid variable takes more than 1 value ...
def gv_impact(n, best_coords, costs, dims, min_cost):
    left_coords = list(best_coords)
    left_coords[n] = left_coords[n] - 1
    right_coords = list(best_coords)
    right_coords[n] = right_coords[n] + 1

    # impact of a grid variable at a given point is the largest magnitude of cost change when that variable
    # shifts one step from its value at that point keeping all others the same
    if best_coords[n] == 0:  # at lower limit so cost only available for an increase
        impact = abs(cost_by_coord(right_coords, costs, dims) - min_cost)
    elif best_coords[n] == dims[n] - 1:  # at upper limit so can only decrease
        impact = abs(cost_by_coord(left_coords, costs, dims) - min_cost)
    else:
        # can increase or decrease one step so take the direction that produces the greater change
        impact = max(abs(cost_by_coord(right_coords, costs, dims) - min_cost),
                     abs(cost_by_coord(left_coords, costs, dims) - min_cost))

    return impact


def cost_by_coord(coords, costs, dims):
    """Return cost for the given grid coordinates, given grid dimensions"""
    idx = np.ravel_multi_index(coords, dims)
    cost = costs[idx]
    return cost


if __name__ == '__main__':
    def test():
        project_name = 'pub21'
        expt_name = 'li_single_sbo_fit_cache'
        features = ('swim_speed',)

        gs = {'tau': geom(5, 2 ** 0.25, 0.04511738),
              'ke_tau_prod_grid': geom(5, 2 ** 0.125, 15.48435358),
              'sr_tau_prod_grid': geom(5, 2 ** 0.5, 30844.21650816),
              }

        costdf = costed_results(project_name=project_name, expt_name=expt_name, features=features)

        costs = costdf.cost
        dims = [len(gval) for gval in gs.values()]

        impacts = gv_impacts(dims, costs)

        print(f'parameter impacts: {impacts}')


    test()
