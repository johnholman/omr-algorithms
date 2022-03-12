from datetime import datetime

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from simulator.sessrun.fit import cost_points, cost_with_gradient
from simulator.sessrun.util import save_data


class Fitter:
    def __init__(self, *, cfg, vcfg, description, actual_summ, derived_parms=None, max_workers=12):
        self.cfg = cfg
        self.vcfg = vcfg
        self.description = description
        self.actual_summ = actual_summ
        self.derived_parms = derived_parms
        self.max_workers = max_workers
        self.features = None
        self.varnames = None
        self.results = []
        self.last_cost = None
        self.costs = []
        self.niter = 0

    def is_parm_name(self, name):
        is_parm = not (
                name.endswith('_grid') or
                name.endswith('_err') or
                name.endswith('_np') or
                name.endswith('_norm') or
                name == 'n' or
                name == 'cost'
        )
        return is_parm

    def cost(self, values):
        costs_df = cost_points([values], self.features, grid_vars=self.varnames, cfg=self.cfg, vcfg=self.vcfg,
                               description=self.description,
                               actual_summ=self.actual_summ,
                               derived_parms=self.derived_parms, max_workers=12, save=False, verbose=False)
        result = costs_df.iloc[0].to_dict()
        cost = result['cost']

        self.results.append(result)
        self.last_cost = result['cost']
        self.costs.append(cost)
        self.niter += 1

        parms = [val for key, val in result.items() if self.is_parm_name(key)]
        fparms = ', '.join((f'{v:.6f}' for v in parms))
        fvalues = ', '.join((f'{v:.6f}' for v in values))
        print(f'\n{self.niter}: values ({fvalues}) model parameters ({fparms}) cost {cost:.6f}\n')

        return cost

    def cost_with_gradient(self, point):
        grad_steps = (0.01, 1, 100)

        cost, cost_grad, costs_df = cost_with_gradient(point=point,
                                                       features=self.features,
                                                       grad_steps=grad_steps,
                                                       grid_vars=self.varnames, cfg=self.cfg,
                                                       vcfg=self.vcfg,
                                                       description=self.description,
                                                       actual_summ=self.actual_summ,
                                                       derived_parms=self.derived_parms, max_workers=12, save=False)
        # accumulate the evaluation results
        result = costs_df.to_dict(orient='records')
        self.results += result
        self.last_cost = cost
        self.costs.append(cost)
        self.niter += 1

        parms = [val for key, val in result[0].items() if self.is_parm_name(key)]
        fparms = ', '.join((f'{v:.6f}' for v in parms))
        fvalues = ', '.join((f'{v:.6f}' for v in point))
        fgrad = ', '.join((f'{v:.4f}' for v in cost_grad))
        print(f'\n{self.niter}: values ({fvalues}) grad ({fgrad}) model parameters ({fparms}) cost {cost:.6f}\n')

        return cost, cost_grad

    def fit(self, point, features):
        self.varnames = tuple(point.keys())
        self.features = features
        values = np.array(tuple(point.values()))
        optresult = self.optimize(values)
        print(optresult)
        fname = 'optfit' + datetime.now().strftime("_%Y-%m-%d_%H%M-%S")
        fit_df = pd.DataFrame(self.results)
        save_data(fit_df, filename='optfit', format='csv')
        save_data(fit_df, filename=fname, format='csv')
        return self.costs, fit_df

    def optimize(self, start_values):
        raise NotImplementedError


class NelderMeadFitter(Fitter):
    def optimize(self, start_values):
        optresult = minimize(self.cost, start_values, method='nelder-mead',
                             options={'xatol': 1e-8, 'disp': True,
                                      'maxfev': 500,
                                      'bounds': ((0.01, 10), (0, None), (0, None))
                                      })
        return optresult


class BFGSNoGradFitter(Fitter):
    def optimize(self, start_values):
        optresult = minimize(self.cost, start_values, method='BFGS',
                             options={'disp': True, 'eps': (0.01, 1, 100)})
        return optresult


class BFGSFitter(Fitter):
    def optimize(self, start_values):
        optresult = minimize(self.cost_with_gradient, start_values, method='BFGS', jac=True,
                             options={'disp': True, })
        return optresult


class GradientDescentFitter(Fitter):
    def optimize(self, start_values):
        optresult = minimize(self.cost, start_values, method='BFGS',
                             options={'disp': True, 'eps': (0.01, 1, 100)})
        return optresult
