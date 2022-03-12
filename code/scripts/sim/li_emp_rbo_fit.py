import matplotlib.pyplot as plt

from simulator.analysis.report import report_comparison, report_fitting_results, indiv_rpt_expt, group_rpt_expt, \
    summary_rpt_expt
from simulator.expt.actual import get_actual_summ
from simulator.reporting.fit_figs import contour_fit_figs
from simulator.sessrun.erunner import run_expt
from simulator.sessrun.fit import grid_search, best_fit

if __name__ == '__main__':
    search = True
    report = False

    description = "rate: P/LI, intensity: empirical values, fit to combined data on bout rate"

    cfg = {
        'environment.classname': 'simulator.environment.freeswim.FreeSwimEnvironment',
        'controller.classname': 'simulator.agent.controller.DualControllerSpecifiedIntensity',
        'boutgenerator.classname': 'simulator.agent.bouts.BoutGenerator',

        'sensory_delay': 0.22,
        'bout_refactory_period': 0.25,

        'Ke': 1.0,
        'Ki': 1.0,
        'Kp': 0.0,
        'k_intensity': 1.0,

        'seed': 0,
        'dt': 0.01,
        'duration': 30,
        'nsubjects': 30,
    }

    # vcfg = {'height': [8, 32, 56], 'stimulus_speed': [4, 6, 8, 10, 12]}
    vcfg_omr = [
        {'height': 8, 'stimulus_speed': 4, 'ibs': 17.0155},
        {'height': 8, 'stimulus_speed': 6, 'ibs': 19.8156},
        {'height': 8, 'stimulus_speed': 8, 'ibs': 29.1701},
        {'height': 8, 'stimulus_speed': 10, 'ibs': 40.7450},
        {'height': 8, 'stimulus_speed': 12, 'ibs': 44.9352},
        {'height': 32, 'stimulus_speed': 4, 'ibs': 14.7073},
        {'height': 32, 'stimulus_speed': 6, 'ibs': 15.5024},
        {'height': 32, 'stimulus_speed': 8, 'ibs': 17.8899},
        {'height': 32, 'stimulus_speed': 10, 'ibs': 22.2553},
        {'height': 32, 'stimulus_speed': 12, 'ibs': 25.3779},
        {'height': 56, 'stimulus_speed': 4, 'ibs': 12.4233},
        {'height': 56, 'stimulus_speed': 6, 'ibs': 14.8242},
        {'height': 56, 'stimulus_speed': 8, 'ibs': 17.4926},
        {'height': 56, 'stimulus_speed': 10, 'ibs': 19.1186},
        {'height': 56, 'stimulus_speed': 12, 'ibs': 20.6032},
    ]

    # basic OMR experiment and baseline flow experiment combined
    vcfg_bf = [
        # {'height': 8, 'stimulus_speed': 0.8, 'ibs': 15.37407783},
        {'height': 8, 'stimulus_speed': 1.6, 'ibs': 9.384704355},
        {'height': 8, 'stimulus_speed': 2.4, 'ibs': 11.9559331},
        {'height': 8, 'stimulus_speed': 3.2, 'ibs': 14.92646097},
        {'height': 8, 'stimulus_speed': 4.0, 'ibs': 19.17895038},
        {'height': 32, 'stimulus_speed': 3.2, 'ibs': 11.03039207},
        {'height': 32, 'stimulus_speed': 6.4, 'ibs': 16.35512581},
        {'height': 32, 'stimulus_speed': 9.6, 'ibs': 23.40081094},
        {'height': 32, 'stimulus_speed': 12.8, 'ibs': 26.70192188},
        {'height': 32, 'stimulus_speed': 16.0, 'ibs': 34.66866214},
        {'height': 56, 'stimulus_speed': 5.6, 'ibs': 13.93479645},
        {'height': 56, 'stimulus_speed': 11.2, 'ibs': 21.29204234},
        {'height': 56, 'stimulus_speed': 16.8, 'ibs': 27.84539531},
        {'height': 56, 'stimulus_speed': 22.4, 'ibs': 32.87905645},
        {'height': 56, 'stimulus_speed': 28, 'ibs': 37.43791552},
    ]

    vcfg = vcfg_bf + vcfg_omr

    # # 1
    # grid_spec = {'gain_rate_grid': [10.0, 100.0, 1000.0],
    #              'tau': [0.0, 0.1, 1.0],
    #              }

    # # 2
    # grid_spec = {'gain_rate_grid': [10.0, 21.544, 46.416, 100.0, 215.443, 464.159, 1000.0],
    #              'tau': [0.01, 0.02, 0.063, 0.2, 0.632, 2.0, 6.325],
    #              }
    #
    # # 3
    # grid_spec = {'gain_rate_grid': [15.811, 23.208, 34.065, 50.0, 73.39, 107.722, 158.114],
    #              'tau': [0.01, 0.02, 0.034, 0.05, 0.073, 0.108, 0.158],
    #              }
    #
    # 4
    grid_spec = {'gain_rate_grid': [25.0, 31.498, 39.685, 50.0, 62.996, 79.37, 100.0],
                 'tau': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07],
                 }

    features = ['bout_rate']

    derived_parms = {
        'k_rate': "gain_rate_grid/tau if tau > 0.01 else gain_rate_grid",
    }

    # compare with combined data from both experiments
    actual_summ = get_actual_summ()

    if search:
        print(f'search grid: {grid_spec}')
        grid_search(grid_spec, cfg, vcfg, description, actual_summ, derived_parms=derived_parms, max_workers=12)

    if report:
        # get parameters and costs from the best fit result
        parms, errs = best_fit(features)

        # add optimised parameters to the fixed ones given above and increased number of subjects
        cfg = {**cfg, **parms}

        # run the simulation with this configuration
        print(f'running simulation with parameters {parms}')
        data = _, df = run_expt(description=description, cfg=cfg, vcfg=vcfg, save=True, verbose=False)

        indiv_rpt_expt(data, groups=[1, 2, 4, 7, 10, 14], period=(25, 27),
                       dep_vars=['sensed_flow', 'u_rate', 'm_rate', 'start_rate', 'start_bout', 'u_intensity',
                                 'swim_speed'])

        indiv_rpt_expt(data, groups=[1, 2, 4, 7, 10, 14], title='20', period=-20,
                       dep_vars=['sensed_flow', 'u_rate', 'motor_integral', 'start_rate', 'start_bout', 'u_intensity',
                                 'swim_speed'])

        group_rpt_expt(data, dep_vars=['smoothed_swim_speed', 'smoothed_omr_ratio'], win_size=100)

        summary_rpt_expt(data, indep_vars=['height', 'stimulus_speed'],
                         dep_vars=['bout_rate', 'bout_init_speed', 'swim_speed', 'omr_ratio', 'num_premature',
                                   'num_subliminal'],
                         period=-20, ncolumns=2,
                         title='last 20 s')

        report_comparison(actual_summ=actual_summ, predicted=data,
                          dep_vars=['bout_rate', 'bout_init_speed', 'swim_speed', 'omr_ratio'],
                          ncolumns=2)

    # error contour plots
    contour_fit_figs(costed_features=features,
                     report_vars=['gain_rate_grid:log', 'tau'])

    # report_fitting_results(features=features, grid_spec=grid_spec, nbest=20)
    report_fitting_results(features=features, grid_spec=grid_spec, nbest=100)

    plt.show()
