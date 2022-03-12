import matplotlib.pyplot as plt

from simulator.analysis.report import report_comparison, report_fitting_results, group_rpt_expt, summary_rpt_expt
from simulator.expt.actual import get_actual_summ
from simulator.reporting.fit_figs import contour_fit_figs
from simulator.sessrun.erunner import run_expt
from simulator.sessrun.fit import grid_search, best_fit

if __name__ == '__main__':
    search = True
    report = False

    description = "immediate optic flow and motor inhibition for rate, LI for intensity" \
                  " fit to combined data on bout rate and intensity " \
                  " omits lowest stimulus speed group, 3 mm/s subliminal filter"

    cfg = {
        'environment.classname': 'simulator.environment.freeswim.FreeSwimEnvironment',
        'controller.classname': 'simulator.agent.controller.DualFactorController',
        'boutgenerator.classname': 'simulator.agent.bouts.BoutGenerator',
        # overall flow controls rate and intensity
        'kf_intensity': 1.0,
        'kb_intensity': 1.0,

        'Ke': 1.0,

        'sensory_delay': 0.22,
        'bout_refactory_period': 0.25,

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

    # compare with combined data from both experiments, but excluding lowest stimulus speed group from BF procedure
    actual_summ = get_actual_summ()

    # # 1 - starting point for fit 3 jun 21 carrying over parameters from limi-emp fit
    # grid_spec = {
    #     'gain_intensity_grid': [1.0, 1.585, 2.512, 3.981, 6.31, 10.0, 15.849, 25.119, 39.811, 63.096, 100.0,
    #                             158.489, 251.189, 398.107, 630.957, 1000.0, 1584.893, 2511.886, 3981.072,
    #                             6309.573, 10000.0],
    #     'gain_motor_grid': [0.064],
    #     'k_rate': [1414.21],
    #     'tau_motor': [0.112],
    #     'tau_intensity': [0.01, 0.014, 0.02, 0.028, 0.04, 0.056, 0.079, 0.112, 0.158, 0.224, 0.316, 0.446,
    #                       0.631, 0.891, 1.258, 1.777, 2.51, 3.546, 5.008, 7.074, 9.993],
    # }
    # # 2
    # grid_spec = {
    #     'gain_intensity_grid': [25.119],
    #     'gain_motor_grid': [0.002, 0.0029, 0.004, 0.0057, 0.0081, 0.0114, 0.0161, 0.0227, 0.0321,
    #       0.0453, 0.064, 0.0904, 0.1277, 0.1804, 0.2548, 0.3599, 0.5084, 0.7181, 1.0143, 1.4328, 2.0239],
    #     'k_rate': [1414.21],
    #     'tau_motor': [0.112],
    #     'tau_intensity': [0.02]
    # }
    # # 3
    # grid_spec = {
    #     'gain_intensity_grid': [25.119],
    #     'gain_motor_grid': [0.064],
    #     'k_rate': [44.7212, 63.1704, 89.2306, 126.0416, 178.0385, 251.4861, 355.2335, 501.7806, 708.784, 1001.184,
    #                1414.21, 1997.6247, 2821.7199, 3985.7853, 5630.0714, 7952.6873, 11233.4693, 15867.6972, 22413.718,
    #                31660.2182, 44721.2469],
    #     'tau_motor': [0.112],
    #     'tau_intensity': [0.02]
    # }
    # # 4
    # grid_spec = {
    #     'gain_intensity_grid': [25.119],
    #     'gain_motor_grid': [0.064],
    #     'k_rate': [708.784],
    #     'tau_motor': [0.0035, 0.005, 0.0071, 0.01, 0.0141, 0.0199, 0.0281, 0.0397, 0.0561, 0.0793, 0.112, 0.1582,
    #                   0.2235, 0.3157, 0.4459, 0.6298, 0.8896, 1.2567, 1.7751, 2.5074, 3.5418],
    #     'tau_intensity': [0.02]
    # }
    # # 5
    # grid_spec = {
    #     'gain_intensity_grid': [7.9433, 14.1255, 25.119, 44.6686, 79.4333],
    #     'gain_motor_grid': [0.0202, 0.036, 0.064, 0.1138, 0.2024],
    #     'k_rate': [708.784],
    #     'tau_motor': [0.112],
    #     'tau_intensity': [0.02]
    # }
    # # 6
    # grid_spec = {
    #     'gain_intensity_grid': [25.119],
    #     'gain_motor_grid': [0.064],
    #     'k_rate': [354.392, 708.784, 1417.568],
    #     'tau_motor': [0.056, 0.112, 0.224],
    #     'tau_intensity': [0.01, 0.02, 0.04]
    # }
    # # 7
    # grid_spec = {
    #     'gain_intensity_grid': [14.1255, 25.119, 44.6686],
    #     'gain_motor_grid': [0.036, 0.064, 0.1138],
    #     'k_rate': [354.392, 708.784, 1417.568],
    #     'tau_motor': [0.056, 0.112, 0.224],
    #     'tau_intensity': [0.01, 0.02, 0.04]
    # }
    # # 8
    # grid_spec = {
    #     'gain_intensity_grid': [17.7618, 25.119, 35.5236],
    #     'gain_motor_grid': [0.0202, 0.036, 0.064],
    #     'k_rate': [354.392, 708.784, 1417.568],
    #     'tau_motor': [0.112, 0.224, 0.448],
    #     'tau_intensity': [0.01, 0.02, 0.04]
    # }
    # # 9
    # grid_spec = {
    #     'gain_intensity_grid': [17.7618, 21.1225, 25.119, 29.8717, 35.5236],
    #     'gain_motor_grid': [0.0255, 0.0303, 0.036, 0.0428, 0.0509],
    #     'k_rate': [708.784],
    #     'tau_motor': [0.224],
    #     'tau_intensity': [0.02]
    # }
    # # 10
    # grid_spec = {
    #     'gain_intensity_grid': [25.119],
    #     'gain_motor_grid': [0.036],
    #     'k_rate': [501.186, 708.784, 1002.3719],
    #     'tau_motor': [0.1584, 0.224, 0.3168],
    #     'tau_intensity': [0.0141, 0.02, 0.0283]
    # }
    # # 11
    # grid_spec = {
    #     'gain_intensity_grid': [17.7618, 21.1225, 25.119, 29.8717, 35.5236],
    #     'gain_motor_grid': [0.0255, 0.0303, 0.036, 0.0428, 0.0509],
    #     'k_rate': [1002.3719],
    #     'tau_motor': [0.3168],
    #     'tau_intensity': [0.0283]
    # }
    # # 12
    # grid_spec = {
    #     'gain_intensity_grid': [25.119],
    #     'gain_motor_grid': [0.036],
    #     'k_rate': [708.784, 842.8909, 1002.3719, 1192.0278, 1417.5679],
    #     'tau_motor': [0.224, 0.2664, 0.3168, 0.3767, 0.448],
    #     'tau_intensity': [0.02, 0.0238, 0.0283, 0.0337, 0.04]
    # }
    # # 13
    # grid_spec = {
    #     'gain_intensity_grid': [17.7618, 21.1225, 25.119, 29.8717, 35.5236],
    #     'gain_motor_grid': [0.0255, 0.0303, 0.036, 0.0428, 0.0509],
    #     'k_rate': [1002.3719],
    #     'tau_motor': [0.2664],
    #     'tau_intensity': [0.0238]
    # }
    # # 14
    # grid_spec = {
    #     'gain_intensity_grid': [17.7618, 25.119, 35.5236],
    #     'gain_motor_grid': [0.0255, 0.036, 0.0509],
    #     'k_rate': [708.784, 1002.3719, 1417.5679],
    #     'tau_motor': [0.1881, 0.266, 0.3762],
    #     'tau_intensity': [0.0168, 0.0238, 0.0337]
    # }
    # # 15
    # grid_spec = {
    #     'gain_intensity_grid': [17.7618, 21.1225, 25.119, 29.8717, 35.5236],
    #     'gain_motor_grid': [0.0214, 0.0255, 0.0303, 0.036, 0.0429],
    #     'k_rate': [708.784, 842.8909, 1002.3719, 1192.0278, 1417.5679],
    #     'tau_motor': [0.1881, 0.2237, 0.266, 0.3163, 0.3762],
    #     'tau_intensity': [0.0168, 0.02, 0.0238, 0.0283, 0.0337]
    # }
    # # 16
    # grid_spec = {
    #     'gain_intensity_grid': [17.7618, 21.1225, 25.119, 29.8717, 35.5236],
    #     'gain_motor_grid': [0.0214, 0.0255, 0.0303, 0.036, 0.0429],
    #     'k_rate': [596.0139, 708.784, 842.891, 1002.372, 1192.0279],
    #     'tau_motor': [0.266, 0.3163, 0.3762, 0.4474, 0.532],
    #     'tau_intensity': [0.0168, 0.02, 0.0238, 0.0283, 0.0337]
    # }
    # # 17
    # grid_spec = {
    #     'gain_intensity_grid': [21.1225, 23.0342, 25.119, 27.3925, 29.8717],
    #     'gain_motor_grid': [0.0255, 0.0278, 0.0303, 0.033, 0.036],
    #     'k_rate': [708.784, 772.9345, 842.891, 919.1792, 1002.372],
    #     'tau_motor': [0.3163, 0.345, 0.3762, 0.4102, 0.4474],
    #     'tau_intensity': [0.02, 0.0218, 0.0238, 0.026, 0.0283]
    # }
    # 18
    grid_spec = {
        'gain_intensity_grid': [21.1225, 23.0342, 25.119, 27.3925, 29.8717],
        'gain_motor_grid': [0.0255, 0.0278, 0.0303, 0.033, 0.036],
        'k_rate': [649.9574, 708.7836, 772.934, 842.8905, 919.1786],
        'tau_motor': [0.2901, 0.3164, 0.345, 0.3762, 0.4103],
        'tau_intensity': [0.02, 0.0218, 0.0238, 0.026, 0.0283]
    }

    derived_parms = {
        'k_motor': "gain_motor_grid/tau_motor if tau_motor > 0.01 else gain_motor_grid",
        'k_intensity': "gain_intensity_grid/tau_intensity if tau_intensity > 0.01 else gain_intensity_grid",
    }

    if search:
        print(f'search grid: {grid_spec}')
        # grid_search(grid_spec, cfg, vcfg, description, actual_summ, derived_parms=derived_parms, max_workers=9)
        grid_search(grid_spec, cfg, vcfg, description, actual_summ, derived_parms=derived_parms, max_workers=15)

    features = ['bout_rate', 'bout_init_speed']

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

    # intensity parameters
    contour_fit_figs(costed_features=features,
                     report_vars=['gain_intensity_grid:log', 'tau_intensity:log'])

    # rate parameters
    contour_fit_figs(costed_features=features,
                     report_vars=['k_rate:log', 'gain_motor_grid:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['k_rate:log', 'tau_motor:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['gain_motor_grid:log', 'tau_motor:log'])

    # rate-intensity interactions
    contour_fit_figs(costed_features=features,
                     report_vars=['gain_intensity_grid:log', 'k_rate:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['gain_intensity_grid:log', 'gain_motor_grid:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['gain_intensity_grid:log', 'tau_motor:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['tau_intensity:log', 'k_rate:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['tau_intensity:log', 'gain_motor_grid:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['tau_intensity:log', 'tau_motor:log'])

    report_fitting_results(features=features, grid_spec=grid_spec, nbest=100)

    plt.show()
