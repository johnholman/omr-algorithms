import matplotlib.pyplot as plt

from simulator.analysis.report import report_comparison, report_fitting_results, group_rpt_expt, summary_rpt_expt
from simulator.expt.actual import get_actual_summ
from simulator.reporting.fit_figs import contour_fit_figs
from simulator.sessrun.erunner import run_expt
from simulator.sessrun.fit import grid_search, best_fit

if __name__ == '__main__':
    search = True
    report = False

    description = "P-only with LI motor inhibition for rate, split FB LI for intensity " \
                  " fit to combined data on bout rate and intensity " \
                  " omits lowest stimulus speed group, 3 mm/s subliminal filter"

    cfg = {
        'environment.classname': 'simulator.environment.freeswim.FreeSwimEnvironment',
        'controller.classname': 'simulator.agent.controller.DualFactorController',
        'boutgenerator.classname': 'simulator.agent.bouts.BoutGenerator',

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

    # # 1
    # grid_spec = {'k_rate': [1414.21],
    #              'gain_motor_grid': [0.064],
    #              'tau_motor': [0.112],
    #              'fgain_intensity_grid': [1.0, 4.642, 21.544, 100.0, 464.159, 2154.435, 10000.0],
    #              'kb_kf_intensity_ratio_grid': [0.003, 0.01, 0.032, 0.1, 0.316, 1.0, 3.162],
    #              'tau_intensity': [0.01, 0.032, 0.1, 0.316, 0.999, 3.16, 9.993],
    #              }
    # # 2
    # grid_spec = {'k_rate': [1414.21],
    #              'gain_motor_grid': [0.064],
    #              'tau_motor': [0.112],
    #              'fgain_intensity_grid': [2.154, 6.813, 21.544, 68.128, 215.44],
    #              'kb_kf_intensity_ratio_grid': [0.01, 0.032, 0.1, 0.316, 1.0],
    #              'tau_intensity': [0.01, 0.032, 0.1, 0.316, 1.0],
    #              }
    # # 3
    # grid_spec = {'k_rate': [141.421, 447.212, 1414.21, 4472.125, 14142.1],
    #              'gain_motor_grid': [0.006, 0.02, 0.064, 0.202, 0.64],
    #              'tau_motor': [0.01, 0.035, 0.112, 0.354, 1.12],
    #              'fgain_intensity_grid': [21.544],
    #              'kb_kf_intensity_ratio_grid': [0.01],
    #              'tau_intensity': [0.01],
    #              }
    # # 4
    # grid_spec = {'k_rate': [447.212],
    #              'gain_motor_grid': [0.064],
    #              'tau_motor': [0.112],
    #              'fgain_intensity_grid': [2.154, 6.813, 21.544, 68.128, 215.44],
    #              'kb_kf_intensity_ratio_grid': [0.01, 0.032, 0.1, 0.316, 1.0],
    #              'tau_intensity': [0.01, 0.032, 0.1, 0.316, 1.0],
    #              }
    # # 5
    # grid_spec = {'k_rate': [447.212],
    #              'gain_motor_grid': [0.064],
    #              'tau_motor': [0.112],
    #              'fgain_intensity_grid': [6.813, 12.115, 21.544, 38.311, 68.128],
    #              'kb_kf_intensity_ratio_grid': [0.01, 0.032, 0.1, 0.316, 1.0],
    #              'tau_intensity': [0.01, 0.032, 0.1, 0.316, 1.0],
    #              }
    # # 6
    # grid_spec = {'k_rate': [44.721, 141.421, 447.212, 1414.209, 4472.12],
    #              'gain_motor_grid': [0.006, 0.02, 0.064, 0.202, 0.64],
    #              'tau_motor': [0.01, 0.035, 0.112, 0.354, 1.12],
    #              'fgain_intensity_grid': [38.311],
    #              'kb_kf_intensity_ratio_grid': [0.032],
    #              'tau_intensity': [0.316],
    #              }
    # # 7
    # grid_spec = {'k_rate': [44.816, 79.696, 141.721, 252.02, 448.161],
    #              'gain_motor_grid': [0.006, 0.011, 0.02, 0.036, 0.063],
    #              'tau_motor': [0.01, 0.035, 0.112, 0.354, 1.12],
    #              'fgain_intensity_grid': [38.311],
    #              'kb_kf_intensity_ratio_grid': [0.032],
    #              'tau_intensity': [0.316],
    #              }
    # # 8
    # grid_spec = {'k_rate': [141.721, 252.02, 448.161],
    #              'gain_motor_grid': [0.011, 0.02, 0.036],
    #              'tau_motor': [0.354, 1.12, 3.542],
    #              'fgain_intensity_grid': [21.544, 38.311, 68.128],
    #              'kb_kf_intensity_ratio_grid': [0.01, 0.032, 0.1],
    #              'tau_intensity': [0.1, 0.316, 1.0],
    #              }
    # # 9
    # grid_spec = {'k_rate': [252.02],
    #              'gain_motor_grid': [0.006, 0.009, 0.014, 0.02, 0.029, 0.043, 0.063],
    #              'tau_motor': [1.12],
    #              'fgain_intensity_grid': [12.115, 17.782, 26.101, 38.311, 56.233, 82.539, 121.15],
    #              'kb_kf_intensity_ratio_grid': [0.032],
    #              'tau_intensity': [0.316],
    #              }
    # # 10
    # grid_spec = {'k_rate': [79.696, 116.977, 171.699, 252.02, 369.915, 542.961, 796.957],
    #              'gain_motor_grid': [0.02],
    #              'tau_motor': [0.158, 0.304, 0.584, 1.12, 2.15, 4.126, 7.92],
    #              'fgain_intensity_grid': [38.311],
    #              'kb_kf_intensity_ratio_grid': [0.032],
    #              'tau_intensity': [0.316],
    #              }
    # # 11
    # grid_spec = {'k_rate': [252.02],
    #              'gain_motor_grid': [0.02],
    #              'tau_motor': [1.12],
    #              'fgain_intensity_grid': [38.311],
    #              'kb_kf_intensity_ratio_grid': [0.003, 0.007, 0.015, 0.032, 0.069, 0.149, 0.32],
    #              'tau_intensity': [0.1, 0.147, 0.215, 0.316, 0.464, 0.681, 1.0],
    #              }
    # # 12
    # grid_spec = {'k_rate': [252.02],
    #              'gain_motor_grid': [0.01, 0.013, 0.016, 0.02, 0.025, 0.032, 0.04],
    #              'tau_motor': [1.12],
    #              'fgain_intensity_grid': [19.156, 24.134, 30.407, 38.311, 48.269, 60.815, 76.622],
    #              'kb_kf_intensity_ratio_grid': [0.015],
    #              'tau_intensity': [0.215],
    #              }
    # # 13
    # grid_spec = {'k_rate': [252.02],
    #              'gain_motor_grid': [0.02],
    #              'tau_motor': [1.12],
    #              'fgain_intensity_grid': [38.311],
    #              'kb_kf_intensity_ratio_grid': [0.005, 0.008, 0.011, 0.015, 0.021, 0.03, 0.042],
    #              'tau_intensity': [0.076, 0.108, 0.152, 0.215, 0.304, 0.43, 0.608],
    #              }
    # # 14
    # grid_spec = {'k_rate': [252.02],
    #              'gain_motor_grid': [0.014, 0.016, 0.018, 0.02, 0.022, 0.025, 0.028],
    #              'tau_motor': [1.12],
    #              'fgain_intensity_grid': [27.09, 30.407, 34.131, 38.311, 43.003, 48.269, 54.18],
    #              'kb_kf_intensity_ratio_grid': [0.021],
    #              'tau_intensity': [0.215],
    #              }

    # # 15
    # grid_spec = {'k_rate': [89.103, 126.01, 178.205, 252.02, 356.41, 504.04, 712.82],
    #              'gain_motor_grid': [0.02],
    #              'tau_motor': [0.396, 0.56, 0.792, 1.12, 1.584, 2.24, 3.168],
    #              'fgain_intensity_grid':  [38.311],
    #              'kb_kf_intensity_ratio_grid': [0.021],
    #              'tau_intensity': [0.215],
    #              }
    # # 16
    # grid_spec = {'k_rate': [178.205, 252.02, 356.41],
    #              'gain_motor_grid': [0.016, 0.02, 0.025],
    #              'tau_motor': [0.792, 1.12, 1.584],
    #              'fgain_intensity_grid': [30.407, 38.311, 48.269],
    #              'kb_kf_intensity_ratio_grid': [0.015, 0.021, 0.03],
    #              'tau_intensity': [0.152, 0.215, 0.304],
    #              }
    # # 17
    # grid_spec = {'k_rate': [252.02, 356.41, 504.04],
    #              'gain_motor_grid': [0.011, 0.016, 0.023],
    #              'tau_motor': [0.792, 1.12, 1.584],
    #              'fgain_intensity_grid': [34.131, 48.269, 68.263],
    #              'kb_kf_intensity_ratio_grid': [0.011, 0.015, 0.021],
    #              'tau_intensity': [0.107, 0.152, 0.215],
    #              }
    # # 18
    # grid_spec = {'k_rate': [356.41],
    #              'gain_motor_grid': [0.016],
    #              'tau_motor': [1.12],
    #              'fgain_intensity_grid': [48.269],
    #              'kb_kf_intensity_ratio_grid': [0.0001, 0.004, 0.005, 0.005, 0.006, 0.007, 0.007, 0.008, 0.009, 0.01,
    #                                             0.011, 0.012, 0.014, 0.015, 0.017, 0.018, 0.021, 0.023, 0.025, 0.028,
    #                                             0.031],
    #              'tau_intensity': [0.152],
    #              }
    # # 19
    # grid_spec = {'k_rate': [252.02, 356.41, 504.04],
    #              'gain_motor_grid': [0.011, 0.016, 0.023],
    #              'tau_motor': [0.792, 1.12, 1.584],
    #              'fgain_intensity_grid': [34.131, 48.269, 68.263],
    #              'kb_kf_intensity_ratio_grid': [0.0, 0.01, 0.02],
    #              'tau_intensity': [0.107, 0.152, 0.215],
    #              }
    # # 20 - picking up from 17 to finish fit (results of 17 used to prime pmi-fli fit)
    # grid_spec = {
    #     'fgain_intensity_grid': [34.131, 40.589, 48.269, 57.402, 68.263],
    #     'gain_motor_grid': [0.011, 0.013, 0.016, 0.019, 0.023],
    #     'k_rate': [356.41],
    #     'tau_motor': [1.12],
    #     'kb_kf_intensity_ratio_grid': [0.011],
    #     'tau_intensity': [0.152],
    # }
    # # 21
    # grid_spec = {
    #     'fgain_intensity_grid': [48.269],
    #     'gain_motor_grid': [0.016],
    #     'k_rate': [252.02, 299.704, 356.41, 423.845, 504.04],
    #     'tau_motor': [0.792, 0.942, 1.12, 1.332, 1.584],
    #     'kb_kf_intensity_ratio_grid': [0.011],
    #     'tau_intensity': [0.152],
    # }
    # # 22
    # grid_spec = {
    #     'fgain_intensity_grid': [48.269],
    #     'gain_motor_grid': [0.016],
    #     'k_rate': [299.704],
    #     'tau_motor': [0.792],
    #     'kb_kf_intensity_ratio_grid': [0.0, 0.0055, 0.011, 0.0165, 0.022],
    #     'tau_intensity': [0.107, 0.128, 0.152, 0.181, 0.215]
    # }
    # # 23
    # grid_spec = {
    #     'fgain_intensity_grid': [34.131, 40.589, 48.269, 57.402, 68.263],
    #     'gain_motor_grid': [0.011, 0.013, 0.016, 0.019, 0.023],
    #     'k_rate': [299.704],
    #     'tau_motor': [0.792],
    #     'kb_kf_intensity_ratio_grid': [0.011],
    #     'tau_intensity': [0.152]
    # }
    # # 24
    # grid_spec = {
    #     'fgain_intensity_grid': [48.269],
    #     'gain_motor_grid': [0.016],
    #     'k_rate': [211.923, 252.02, 299.704, 356.41, 423.845],
    #     'tau_motor': [0.56, 0.666, 0.792, 0.942, 1.12],
    #     'kb_kf_intensity_ratio_grid': [0.011],
    #     'tau_intensity': [0.152]
    # }
    # # 25
    # grid_spec = {
    #     'fgain_intensity_grid': [48.269],
    #     'gain_motor_grid': [0.016],
    #     'k_rate': [252.02],
    #     'tau_motor': [0.56],
    #     'kb_kf_intensity_ratio_grid': [0.0, 0.0055, 0.011, 0.0165, 0.022],
    #     'tau_intensity': [0.107, 0.128, 0.152, 0.181, 0.215]
    # }
    # # 26
    # grid_spec = {
    #     'fgain_intensity_grid': [34.131, 40.589, 48.269, 57.402, 68.263],
    #     'gain_motor_grid': [0.011, 0.013, 0.016, 0.019, 0.023],
    #     'k_rate': [252.02],
    #     'tau_motor': [0.56],
    #     'kb_kf_intensity_ratio_grid': [0.011],
    #     'tau_intensity': [0.152]
    # }
    # # 27
    # grid_spec = {
    #     'fgain_intensity_grid': [48.269],
    #     'gain_motor_grid': [0.016],
    #     'k_rate': [178.205, 211.923, 252.02, 299.704, 356.41],
    #     'tau_motor': [0.396, 0.471, 0.56, 0.666, 0.792],
    #     'kb_kf_intensity_ratio_grid': [0.011],
    #     'tau_intensity': [0.152]
    # }
    # # 28 - full fit at 3 level 1:sqrt(2)
    # grid_spec = {
    #     'fgain_intensity_grid': [40.589, 48.269, 57.402],
    #     'gain_motor_grid': [0.013, 0.016, 0.019],
    #     'k_rate': [211.923, 252.02, 299.704],
    #     'tau_motor': [0.471, 0.56, 0.666],
    #     'kb_kf_intensity_ratio_grid': [0.0, 0.0055, 0.011, 0.0165],
    #     'tau_intensity': [0.128, 0.152, 0.181]
    # }
    # # 29
    # grid_spec = {
    #     'fgain_intensity_grid': [34.131, 40.589, 48.269],
    #     'gain_motor_grid': [0.016, 0.019, 0.023],
    #     'k_rate': [178.205, 211.923, 252.02],
    #     'tau_motor': [0.471, 0.56, 0.666],
    #     'kb_kf_intensity_ratio_grid': [0.0, 0.0055, 0.011],
    #     'tau_intensity': [0.128, 0.152, 0.181]
    # }
    # # 30
    # grid_spec = {
    #     'fgain_intensity_grid': [34.131, 37.22, 40.589, 44.263, 48.269],
    #     'gain_motor_grid': [0.016, 0.017, 0.019, 0.021, 0.023],
    #     'k_rate': [211.923],
    #     'tau_motor': [0.56],
    #     'tau_intensity': [0.152],
    #     'kb_kf_intensity_ratio_grid': [0.0]
    # }
    # # 31
    # grid_spec = {
    #     'fgain_intensity_grid': [40.589],
    #     'gain_motor_grid': [0.019],
    #     'k_rate': [178.205, 194.334, 211.923, 231.104, 252.02],
    #     'tau_motor': [0.471, 0.514, 0.56, 0.611, 0.666],
    #     'tau_intensity': [0.152],
    #     'kb_kf_intensity_ratio_grid': [0.0]
    # }
    # # 32
    # grid_spec = {
    #     'fgain_intensity_grid': [40.589],
    #     'gain_motor_grid': [0.019],
    #     'k_rate': [231.104],
    #     'tau_motor': [0.666],
    #     'tau_intensity': [0.128, 0.139, 0.152, 0.166, 0.181],
    #     'kb_kf_intensity_ratio_grid': [0.0, 0.00275, 0.0055 , 0.00825, 0.011],
    # }
    # # 33
    # grid_spec = {
    #     'fgain_intensity_grid': [34.131, 37.22, 40.589, 44.263, 48.269],
    #     'gain_motor_grid': [0.016, 0.017, 0.019, 0.021, 0.023],
    #     'k_rate': [231.104],
    #     'tau_motor': [0.666],
    #     'tau_intensity': [0.152],
    #     'kb_kf_intensity_ratio_grid': [0.0],
    # }
    # # 34
    # grid_spec = {
    #     'fgain_intensity_grid': [40.589],
    #     'gain_motor_grid': [0.019],
    #     'k_rate': [194.335, 211.923, 231.104, 252.021, 274.831],
    #     'tau_motor': [0.56, 0.611, 0.666, 0.726, 0.792],
    #     'tau_intensity': [0.152],
    #     'kb_kf_intensity_ratio_grid': [0.0],
    # }
    # # 35
    # grid_spec = {
    #     'fgain_intensity_grid': [40.589],
    #     'gain_motor_grid': [0.019],
    #     'k_rate': [274.831],
    #     'tau_motor': [0.792],
    #     'tau_intensity': [0.128, 0.139, 0.152, 0.166, 0.181],
    #     'kb_kf_intensity_ratio_grid': [0.0, 0.00275, 0.0055 , 0.00825, 0.011],
    # }
    # # 36
    # grid_spec = {
    #     'fgain_intensity_grid': [34.131, 37.22, 40.589, 44.263, 48.269],
    #     'gain_motor_grid': [0.016, 0.017, 0.019, 0.021, 0.023],
    #     'k_rate': [274.831],
    #     'tau_motor': [0.792],
    #     'tau_intensity': [0.152],
    #     'kb_kf_intensity_ratio_grid': [0.0],
    # }
    # # 37
    # grid_spec = {
    #     'fgain_intensity_grid': [44.263],
    #     'gain_motor_grid': [0.017],
    #     'k_rate': [231.104, 252.021, 274.831, 299.705, 326.831],
    #     'tau_motor': [0.666, 0.726, 0.792, 0.864, 0.942],
    #     'tau_intensity': [0.152],
    #     'kb_kf_intensity_ratio_grid': [0.0],
    # }
    # # 38
    # grid_spec = {
    #     'fgain_intensity_grid': [44.263],
    #     'gain_motor_grid': [0.017],
    #     'k_rate': [274.831],
    #     'tau_motor': [0.792],
    #     'tau_intensity': [0.128, 0.139, 0.152, 0.166, 0.181],
    #     'kb_kf_intensity_ratio_grid': [0.0, 0.00275, 0.0055 , 0.00825, 0.011],
    # }
    # # 39
    # grid_spec = {
    #     'fgain_intensity_grid': [37.221, 40.589, 44.263, 48.269, 52.638],
    #     'gain_motor_grid': [0.014, 0.016, 0.017, 0.019, 0.02],
    #     'k_rate': [274.831],
    #     'tau_motor': [0.792],
    #     'tau_intensity': [0.152],
    #     'kb_kf_intensity_ratio_grid': [0.00275],
    # }
    # # 40
    # grid_spec = {
    #     'fgain_intensity_grid': [44.263],
    #     'gain_motor_grid': [0.017],
    #     'k_rate': [231.104, 252.021, 274.831, 299.705, 326.831],
    #     'tau_motor': [0.666, 0.726, 0.792, 0.864, 0.942],
    #     'tau_intensity': [0.152],
    #     'kb_kf_intensity_ratio_grid': [0.00275],
    # }
    # # 41 - full fit at 1:sqrt(2) with new centres
    # grid_spec = {
    #     'fgain_intensity_grid': [37.221, 44.263, 52.638],
    #     'gain_motor_grid': [0.014, 0.017, 0.02],
    #     'k_rate': [231.104, 274.831, 326.831],
    #     'tau_motor': [0.666, 0.792, 0.942],
    #     'tau_intensity': [0.128, 0.152, 0.181],
    #     'kb_kf_intensity_ratio_grid': [0.0, 0.00275, 0.0055]
    # }

    # # 42
    # grid_spec = {
    #     'fgain_intensity_grid': [37.2206, 40.5893, 44.263, 48.2691, 52.6379],
    #     'gain_motor_grid': [0.0143, 0.0156, 0.017, 0.0185, 0.0202],
    #     'k_rate': [231.1044, 252.0211, 274.831, 299.7053, 326.831],
    #     'tau_motor': [0.666, 0.7263, 0.792, 0.8637, 0.9419],
    #     'tau_intensity': [0.1278, 0.1394, 0.152, 0.1658, 0.1808],
    #     'kb_kf_intensity_ratio_grid': [0.0, 0.001375, 0.00275, 0.004125, 0.0055]
    # }
    # 43
    grid_spec = {
        'fgain_intensity_grid': [37.2206, 40.5893, 44.263, 48.2691, 52.6379],
        'gain_motor_grid': [0.0143, 0.0156, 0.017, 0.0185, 0.0202],
        'k_rate': [231.1044, 252.0211, 274.831, 299.7053, 326.831],
        'tau_motor': [0.666, 0.7263, 0.792, 0.8637, 0.9419],
        'tau_intensity': [0.1278, 0.1394, 0.152, 0.1658, 0.1808],
        'kb_kf_intensity_ratio_grid': [0.0, 0.000688, 0.001375, 0.00206, 0.00275],
    }

    features = ['bout_rate', 'bout_init_speed']

    derived_parms = {
        'k_motor': "gain_motor_grid/tau_motor if tau_motor > 0.01 else gain_motor_grid",
        'kf_intensity': "fgain_intensity_grid/tau_intensity if tau_intensity > 0.01 else fgain_intensity_grid",
        'kb_intensity': "fgain_intensity_grid * kb_kf_intensity_ratio_grid / tau_intensity if tau_intensity > 0.01"
                        "else fgain_intensity_grid * kb_kf_intensity_ratio_grid"
    }

    # compare with combined data from both experiments, but excluding lowest stimulus speed group from BF procedure
    actual_summ = get_actual_summ()

    if search:
        print(f'search grid: {grid_spec}')
        grid_search(grid_spec, cfg, vcfg, description, actual_summ, derived_parms=derived_parms, max_workers=13)

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

    contour_fit_figs(costed_features=features,
                     report_vars=['fgain_intensity_grid:log', 'kb_kf_intensity_ratio_grid'])

    contour_fit_figs(costed_features=features,
                     report_vars=['kb_kf_intensity_ratio_grid', 'tau_intensity:log'])

    # rate-intensity interactions
    contour_fit_figs(costed_features=features,
                     report_vars=['k_rate:log', 'fgain_intensity_grid:log', ])

    contour_fit_figs(costed_features=features,
                     report_vars=['k_rate:log', 'tau_intensity:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['k_rate:log', 'kb_kf_intensity_ratio_grid'])

    contour_fit_figs(costed_features=features,
                     report_vars=['gain_motor_grid:log', 'fgain_intensity_grid'])

    contour_fit_figs(costed_features=features,
                     report_vars=['gain_motor_grid:log', 'tau_intensity:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['gain_motor_grid:log', 'kb_kf_intensity_ratio_grid'])

    contour_fit_figs(costed_features=features,
                     report_vars=['tau_motor:log', 'fgain_intensity_grid:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['tau_motor:log', 'tau_intensity:log'])

    contour_fit_figs(costed_features=features,
                     report_vars=['tau_motor:log', 'kb_kf_intensity_ratio_grid'])

    report_fitting_results(features=features, grid_spec=grid_spec, nbest=100)

    plt.show()
