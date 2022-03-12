import matplotlib.pyplot as plt

from simulator.analysis.report import report_comparison, report_fitting_results, group_rpt_expt, summary_rpt_expt
from simulator.expt.actual import get_actual_summ
from simulator.reporting.fit_figs import contour_fit_figs
from simulator.sessrun.erunner import run_expt
from simulator.sessrun.fit import grid_search, best_fit

if __name__ == '__main__':
    search = True
    report = False

    description = "LI optical flow and motor inhibition for rate, empirical mean intensities" \
                  " fit to combined data on bout rate" \
                  " omits lowest stimulus speed condition, 3 mm/s subliminal filter"

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
    # grid_spec = {'gain_rate_grid': [1.0, 10.0, 100.0, 1000.0, 10000.0],
    #              'tau': [0.01, 0.056, 0.316, 1.778, 10.0],
    #              'km_kr_ratio_grid': [0.01, 0.032, 0.1, 0.316, 1.0],
    #              'tau_motor': [0.01, 0.056, 0.316, 1.778, 10.0],
    #              }
    # # 2
    # grid_spec = {'gain_rate_grid': [1000.0, 3162.278, 10000.0, 31622.777, 100000.0],
    #              'tau': [0.01, 0.032, 0.1],
    #              'gain_motor_grid': [0.01, 0.018, 0.032, 0.057, 0.101],
    #              'tau_motor': [0.1, 0.316, 1.0],
    #              }
    # # 3
    # grid_spec = {'gain_rate_grid': [1000.0, 1778.279, 3162.278, 5623.413, 10000.0],
    #              'tau': [0.01, 0.032, 0.1],
    #              'gain_motor_grid': [0.018, 0.032, 0.057],
    #              'tau_motor': [0.1, 0.178, 0.316, 0.562, 1.0],
    #              }
    # # 4
    # grid_spec = {'gain_rate_grid': [1778.279, 3162.278, 5623.413],
    #              'tau': [0.01, 0.02, 0.03],
    #              'gain_motor_grid': [0.016, 0.022, 0.032, 0.045, 0.063],
    #              'tau_motor': [0.158, 0.224, 0.316, 0.447, 0.632],
    #              }
    # # 5
    # grid_spec = {'gain_rate_grid': [1000.0, 1778.279, 3162.277],
    #              'tau': [0.01, 0.02],
    #              'gain_motor_grid': [0.023, 0.032, 0.045, 0.064, 0.091],
    #              'tau_motor': [0.079, 0.112, 0.158, 0.223, 0.316],
    #              }
    # # 6
    # grid_spec = {'gain_rate_grid': [500.0, 707.107, 1000.0, 1414.214, 2000.0],
    #              'tau': [0.01, 0.02],
    #              'gain_motor_grid': [0.032, 0.045, 0.064, 0.091, 0.128],
    #              'tau_motor': [0.056, 0.079, 0.112, 0.158, 0.224],
    #              }
    # # 7
    # grid_spec = {'gain_rate_grid': [500.0, 707.107, 1000.0, 1414.214, 2000.0],
    #              'tau': [0.01, 0.02, 0.04, 0.08, 0.16],
    #              'gain_motor_grid': [0.032, 0.045, 0.064, 0.091, 0.128],
    #              'tau_motor': [0.056, 0.079, 0.112, 0.158, 0.224],
    #              }
    #
    # 8
    grid_spec = {'gain_rate_grid': [707.107, 1000.0, 1414.214, 2000.0, 2828.428],
                 'tau': [0.01, 0.02, 0.04, 0.08, 0.16],
                 'gain_motor_grid': [0.032, 0.045, 0.064, 0.091, 0.128],
                 'tau_motor': [0.056, 0.079, 0.112, 0.158, 0.224],
                 }

    derived_parms = {
        'k_rate': "gain_rate_grid/tau if tau > 0.01 else gain_rate_grid",
        'k_motor': "gain_motor_grid/tau_motor if tau_motor > 0.01 else gain_motor_grid",
    }

    # compare with combined data from both experiments
    actual_summ = get_actual_summ()

    if search:
        print(f'search grid: {grid_spec}')
        grid_search(grid_spec, cfg, vcfg, description, actual_summ, derived_parms=derived_parms, max_workers=12)

    features = ['bout_rate']

    if report:
        # get parameters and costs from the best fit result
        parms, errs = best_fit(features)

        # add optimised parameters to the fixed ones given above and increased number of subjects
        cfg = {**cfg, **parms}

        # run the simulation with this configuration
        print(f'running simulation with parameters {parms}')
        data = _, df = run_expt(description=description, cfg=cfg, vcfg=vcfg, save=True, verbose=False)

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
    contour_fit_figs(costed_features=features, display_features=['bout_rate', 'swim_speed'],
                     report_vars=['gain_rate_grid:log', 'gain_motor_grid:log'])

    contour_fit_figs(costed_features=features, display_features=['bout_rate', 'swim_speed'],
                     report_vars=['gain_rate_grid:log', 'tau:log'])

    contour_fit_figs(costed_features=features, display_features=['bout_rate', 'swim_speed'],
                     report_vars=['gain_rate_grid:log', 'tau_motor:log'])

    contour_fit_figs(costed_features=features, display_features=['bout_rate', 'swim_speed'],
                     report_vars=['gain_motor_grid:log', 'tau_motor:log'])

    # report_fitting_results(features=features, grid_spec=grid_spec, nbest=20)
    report_fitting_results(features=features, grid_spec=grid_spec, nbest=100)

    plt.show()
