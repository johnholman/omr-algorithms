import matplotlib.pyplot as plt

from simulator.analysis.report import report_comparison, report_fitting_results, group_rpt_expt, summary_rpt_expt
from simulator.expt.actual import get_actual_summ
from simulator.reporting.fit_figs import contour_fit_figs
from simulator.sessrun.erunner import run_expt
from simulator.sessrun.fit import grid_search, best_fit

if __name__ == '__main__':
    search = True
    report = False

    description = "P-only with LI motor inhibition for rate, split F-only LI for intensity " \
                  " fit to combined data on bout rate and intensity " \
                  " omits lowest stimulus speed group, 3 mm/s subliminal filter"

    cfg = {
        'environment.classname': 'simulator.environment.freeswim.FreeSwimEnvironment',
        'controller.classname': 'simulator.agent.controller.DualFactorController',
        'boutgenerator.classname': 'simulator.agent.bouts.BoutGenerator',

        'kb_intensity': 0.0,

        'sensory_delay': 0.22,
        'bout_refactory_period': 0.25,
        'Ke': 1.0,

        'seed': 0,
        'dt': 0.01,
        'duration': 30,
        'nsubjects': 30,
    }

    # basic OMR experiment and baseline flow experiment combined, with lowest speed condition excluded
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

    # # 1 - initial grid carried over from pmi_fbli_ribo_fit but with kb_intensity set to zero
    # grid_spec = {
    #     'fgain_intensity_grid': [37.221, 44.263, 52.638],
    #     'gain_motor_grid': [0.014, 0.017, 0.02],
    #     'k_rate': [231.104, 274.831, 326.831],
    #     'tau_motor': [0.666, 0.792, 0.942],
    #     'tau_intensity': [0.128, 0.152, 0.181]
    # }
    # # 2.
    # grid_spec = {
    #     'fgain_intensity_grid': [37.221, 40.589, 44.263, 48.269, 52.638],
    #     'gain_motor_grid': [0.0143, 0.0156, 0.017, 0.0185, 0.0202],
    #     'k_rate': [274.831],
    #     'tau_motor': [0.792],
    #     'tau_intensity': [0.152]
    # }
    # # 3.
    # grid_spec = {
    #     'fgain_intensity_grid': [44.263],
    #     'gain_motor_grid': [0.017],
    #     'k_rate': [252.0211, 274.831, 299.7053],
    #     'tau_motor': [0.7263, 0.792, 0.8637],
    #     'tau_intensity': [0.1394, 0.152, 0.1658]
    # }
    # # 4.
    # grid_spec = {
    #     'fgain_intensity_grid': [44.263],
    #     'gain_motor_grid': [0.017],
    #     'k_rate': [231.1044, 252.0211, 274.831, 299.7053, 326.831],
    #     'tau_motor': [0.666, 0.7263, 0.792, 0.8637, 0.9419],
    #     'tau_intensity': [0.152]
    # }
    # # 5.
    # grid_spec = {
    #     'fgain_intensity_grid': [44.263],
    #     'gain_motor_grid': [0.017],
    #     'k_rate': [274.831],
    #     'tau_motor': [0.792],
    #     'tau_intensity': [0.1278, 0.1394, 0.152, 0.1658, 0.1808]
    # }
    # 6 - full grid to confirm
    grid_spec = {
        'fgain_intensity_grid': [37.2206, 40.5893, 44.263, 48.2691, 52.6379],
        'gain_motor_grid': [0.0143, 0.0156, 0.017, 0.0185, 0.0202],
        'k_rate': [231.1044, 252.0211, 274.831, 299.7053, 326.831],
        'tau_motor': [0.666, 0.7263, 0.792, 0.8637, 0.9419],
        'tau_intensity': [0.1278, 0.1394, 0.152, 0.1658, 0.1808]
    }
    # # test with central point only - 1 mar 22
    #
    # grid_spec = {
    #     'fgain_intensity_grid': [44.263],
    #     'gain_motor_grid': [0.017],
    #     'k_rate': [274.831],
    #     'tau_motor': [0.792],
    #     'tau_intensity': [0.152]
    # }
    #
    # # 6 - test with reduced 3-level grid - 5 mar 22
    # grid_spec = {
    #     'fgain_intensity_grid': [40.5893, 44.263, 48.2691],
    #     'gain_motor_grid': [0.0156, 0.017, 0.0185],
    #     'k_rate': [252.0211, 274.831, 299.7053],
    #     'tau_motor': [0.7263, 0.792, 0.8637],
    #     'tau_intensity': [0.1394, 0.152, 0.1658]
    # }

    features = ['bout_rate', 'bout_init_speed']

    derived_parms = {
        'k_motor': "gain_motor_grid/tau_motor if tau_motor > 0.01 else gain_motor_grid",
        'kf_intensity': "fgain_intensity_grid/tau_intensity if tau_intensity > 0.01 else fgain_intensity_grid"
    }

    # compare with combined data from both experiments, but excluding lowest stimulus speed group from BF procedure
    actual_summ = get_actual_summ()

    if search:
        print(f'search grid: {grid_spec}')
        grid_search(grid_spec, cfg, vcfg, description, actual_summ, derived_parms=derived_parms, max_workers=14)

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

    # rate parameters
    contour_fit_figs(costed_features=features,
                     report_vars=['k_rate:log', 'gain_motor_grid:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['k_rate:log', 'tau_motor:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['gain_motor_grid:log', 'tau_motor:log'])

    # intensity parameters
    contour_fit_figs(costed_features=features,
                     report_vars=['fgain_intensity_grid:log', 'tau_intensity:log'])

    # rate-intensity interactions
    contour_fit_figs(costed_features=features,
                     report_vars=['k_rate:log', 'fgain_intensity_grid:log', ])

    contour_fit_figs(costed_features=features,
                     report_vars=['k_rate:log', 'tau_intensity:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['gain_motor_grid:log', 'fgain_intensity_grid'])

    contour_fit_figs(costed_features=features,
                     report_vars=['gain_motor_grid:log', 'tau_intensity:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['tau_motor:log', 'fgain_intensity_grid:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['tau_motor:log', 'tau_intensity:log'])

    report_fitting_results(features=features, grid_spec=grid_spec, nbest=100)

    plt.show()
