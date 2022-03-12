import matplotlib.pyplot as plt

from simulator.analysis.report import report_comparison, report_fitting_results
from simulator.expt.actual import get_actual_summ
from simulator.reporting.fit_figs import contour_fit_figs
from simulator.sessrun.erunner import run_expt
from simulator.sessrun.fit import grid_search, best_fit

if __name__ == '__main__':
    search = True
    report = False

    description = "single process LI with RELU poisson profiled intensity, " \
                  "fitting to combined data on swim speed only" \
                  " subliminal bout filter at 3 mm/s initial speed, omit slowest stimulus speed group"

    cfg = {
        'environment.classname': 'simulator.environment.freeswim.FreeSwimEnvironment',
        'controller.classname': 'simulator.agent.controller.PIController',
        'boutgenerator.classname': 'simulator.agent.bouts.BoutGenerator',

        'sensory_delay': 0.22,
        'Kp': 0.0,
        'Ki': 1.0,
        'Ke': 1.0,

        'bout_refactory_period': 0.25,

        'seed': 0,
        'dt': 0.01,
        'duration': 30,
        'nsubjects': 30,
    }

    # basic OMR experiment and baseline flow experiment combined
    vcfg_bf = [
        # {'height': 8, 'stimulus_speed': 0.8},
        {'height': 8, 'stimulus_speed': 1.6},
        {'height': 8, 'stimulus_speed': 2.4},
        {'height': 8, 'stimulus_speed': 3.2},
        {'height': 8, 'stimulus_speed': 4.0},
        {'height': 32, 'stimulus_speed': 3.2},
        {'height': 32, 'stimulus_speed': 6.4},
        {'height': 32, 'stimulus_speed': 9.6},
        {'height': 32, 'stimulus_speed': 12.8},
        {'height': 32, 'stimulus_speed': 16.0},
        {'height': 56, 'stimulus_speed': 5.6},
        {'height': 56, 'stimulus_speed': 11.2},
        {'height': 56, 'stimulus_speed': 16.8},
        {'height': 56, 'stimulus_speed': 22.4},
        {'height': 56, 'stimulus_speed': 28},
    ]

    vcfg_omr = [
        {'height': 8, 'stimulus_speed': 4},
        {'height': 8, 'stimulus_speed': 6},
        {'height': 8, 'stimulus_speed': 8},
        {'height': 8, 'stimulus_speed': 10},
        {'height': 8, 'stimulus_speed': 12},
        {'height': 32, 'stimulus_speed': 4},
        {'height': 32, 'stimulus_speed': 6},
        {'height': 32, 'stimulus_speed': 8},
        {'height': 32, 'stimulus_speed': 10},
        {'height': 32, 'stimulus_speed': 12},
        {'height': 56, 'stimulus_speed': 4},
        {'height': 56, 'stimulus_speed': 6},
        {'height': 56, 'stimulus_speed': 8},
        {'height': 56, 'stimulus_speed': 10},
        {'height': 56, 'stimulus_speed': 12},
    ]

    vcfg = vcfg_bf + vcfg_omr

    # # 1
    # grid_spec = {'tau': [0.01, 0.05, 0.5, 5],
    #              'ke_tau_prod_grid': [1.0, 10.0, 100.0, 1000.0],
    #              'sr_tau_prod_grid': [1.0, 10.0, 100.0, 1000.0],
    #              }
    # # 2
    # grid_spec = {'tau': [0.01, 0.05, 0.5],
    #              'ke_tau_prod_grid': [1.0, 10.0, 100.0],
    #              'sr_tau_prod_grid': [100.0, 1000.0, 10000.0],
    #              }
    # # 3
    # grid_spec = {'tau': [0.005, 0.016, 0.05, 0.158, 0.5],
    #              'ke_tau_prod_grid': [1.0, 3.162, 10.0, 31.623, 100.0],
    #              'sr_tau_prod_grid': [1000.0, 10000.0, 100000.0],
    #              }
    # # 4
    # grid_spec = {'tau': [0.05, 0.158, 0.5, 1.581, 5.0],
    #              'ke_tau_prod_grid': [10.0, 17.783, 31.623, 56.235, 100.001],
    #              'sr_tau_prod_grid': [1000.0, 10000.0, 100000.0],
    #              }
    # # 5
    # grid_spec = {'tau': [0.01, 0.02, 0.05, 0.121, 0.292, 0.707],
    #              'ke_tau_prod_grid': [10.0, 17.783, 31.623],
    #              'sr_tau_prod_grid': [3162.278, 10000.0, 31622.777],
    #              }
    # # 6
    # grid_spec = {'tau': [0.016, 0.028, 0.05, 0.089, 0.158],
    #              'ke_tau_prod_grid': [10.267, 13.512, 17.783, 23.404, 30.801],
    #              'sr_tau_prod_grid': [1000.001, 1778.281, 3162.28, 5623.417, 10000.007],
    #              }
    # # 7
    # grid_spec = {'tau': [0.025, 0.035, 0.05, 0.071, 0.1],
    #              'ke_tau_prod_grid': [13.512, 17.783, 23.404],
    #              'sr_tau_prod_grid': [889.14, 1257.434, 1778.28, 2514.868, 3556.56],
    #              }
    # 8
    grid_spec = {'tau': [0.05, 0.071, 0.1],
                 'ke_tau_prod_grid': [13.512, 17.783, 23.404],
                 'sr_tau_prod_grid': [1778.28, 2514.868, 3556.56, 5029.735, 7113.12],
                 }

    derived_parms = {
        'k_intensity': "ke_tau_prod_grid/tau if tau > 0.01 else ke_tau_prod_grid",
        'k_rate': "sr_tau_prod_grid/tau if tau > 0.01 else sr_tau_prod_grid",
    }

    # features = ['bout_rate', 'bout_init_speed']
    features = ['swim_speed']

    # # compare with combined data from both experiments
    actual_summ = get_actual_summ()

    if search:
        print(f'search grid: {grid_spec}')
        grid_search(grid_spec, cfg, vcfg, description, actual_summ, derived_parms=derived_parms, max_workers=12)

    if report:
        # get parameters and costs from the best fit result
        parms, errs = best_fit(features)

        # add optimised parameters to the fixed ones given above and increased number of subjects
        cfg = {**cfg, **parms, 'nsubjects': 30}

        # run the simulation with this configuration
        print(f'running simulation with parameters {parms}')
        data = _, df = run_expt(description=description, cfg=cfg, vcfg=vcfg, save=True, verbose=False)

        report_comparison(actual_summ=actual_summ, predicted=data, ncolumns=2,
                          dep_vars=['swim_speed', 'omr_ratio', 'bout_rate', 'bout_dist', ])

    contour_fit_figs(costed_features=features,
                     report_vars=['ke_tau_prod_grid:log', 'tau:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['ke_tau_prod_grid:log', 'sr_tau_prod_grid:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['sr_tau_prod_grid:log', 'tau:log'])

    report_fitting_results(features=features, grid_spec=grid_spec, nbest=50)

    print('finished')

    plt.show()
