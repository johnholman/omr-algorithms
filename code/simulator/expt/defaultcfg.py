# default configuration for the OMR simulations

base_data_folder = '../data'

# default actual experiment data access
# actual = {
#     'base_folder': '../data/expt',
#     'type_map': {
#         'OR': 'or_test',
#         'BF': 'bf_test',
#         'ALL': 'all'
#     }
# }
#
actual = {
    'base_folder': '../data/expt',
    'type_map': {
        'OR': 'or',
        'BF': 'bf',
        'ALL': 'all'
    }
}

# default simulation experiment configuration
experiment = {
    'seed': 1,  # seed for random number generator
    'phases': [1],
    'session.classname': 'simulator.expt.session.Session',
    'agent.classname': 'simulator.agent.agent.Agent',
    'body.classname': 'simulator.agent.body.Body',
    'comparison_summary_fn': 'simulator.analysis.summary.summarise_groups_for_comparison',
    # summarising function for comparisons

    'bout_profile':
        [0.859041, 1.20423, 1.88374, 2.88091, 4.24154, 5.44247, 6.2388, 6.66873, 6.74654, 6.40729, 5.7522, 4.94751,
         4.1325, 3.41497, 2.82952, 2.38261, 2.01852, 1.72298, 1.58602, 1.47212, 1.15671, 0.949774, 0.994968, 0.988332,
         0.904344, 0.836326, 0.779084, 0.732303, 0.690833, 0.652548, 0.618365, 0.589213, 0.559465, 0.539585, 0.519655,
         0.495932, 0.47606, 0.452639, 0.432209, 0.41709, 0.404598, 0.390352, 0.375419, 0.361728, 0.352823, 0.34462,
         0.331954, 0.321193, 0.310516, 0.300199, 0.291429, 0.285913, 0.280799, 0.279977, 0.268588, 0.25762, 0.249043,
         0.245443, 0.244508, 0.23836, 0.230254, 0.232154, 0.227474, 0.223719, 0.216839, 0.207795, 0.212038, 0.203275,
         0.197145, 0.199881, 0.195246, 0.186381, 0.18489, 0.188045, 0.185717, 0.187441, 0.176846, 0.174134, 0.182981,
         0.177213, 0.167138, 0.169459, 0.174625, 0.167913, 0.169341, 0.170584, 0.172266, 0.178018, 0.161502, 0.15377,
         0.157646, 0.162271, 0.171067, 0.163187, 0.157499, 0.159917, 0.147597, 0.149487, 0.153285, 0.1512],
    # scaling factor for a bout with unit initial intensity calculated as 10/sum(bout_profile[:10])
    'ibs_to_scale': 0.23488905285710707,

    # session parameters
    'dt': 0.01,
    'ntrials': 1,
    'nsubjects': 20,
    'duration': 30,
}

# default reporting configuration
report = {
    # default dependent variables to plot for different report types
    'summary_dep_vars': ['swim_speed', 'ground_speed', 'omr_ratio', 'ssbf_ratio'],
    'groups_traj_dep_vars': ['smoothed_swim_speed', 'position', 'smoothed_ssbf_ratio', 'smoothed_omr_ratio'],
    'indiv_traj_dep_vars': ['optic_flow', 'integral_error', 'motor_drive', 'motor_output', 'swim_speed', 'position'],

    # variables to join on when comparing experimental and synthetic data
    'join_vars': ['height_category', 'stimulus_speed'],

    # data features to compare between experimental and synthetic data
    'comparison_vars': ['swim_speed', 'omr_ratio', 'ssbf_ratio', 'bout_rate', 'bout_dist', 'bout_init_speed'],

    # default mapping from variable names to labels
    'default_label_map': {
        'start_rate': 'Poisson rate (Hz)',
        'swim_speed': 'swim speed (mm/s)',
        'ground_speed': 'SOG (ground_speed) (mm/s)',
        'stimulus_speed': 'stimulus speed (mm/s)',
        'integral_error': 'ierr',
        'integrated_flow': 'integrated flow',
        'motor_output': 'motor output',
        'optic_flow': 'flow (rad/s)',
        'sensed_flow': 'sensed flow\n(rad/s)',
        'f_rate': 'flow facilitation',
        'm_rate': 'motor inhibition',
        'intensity_flow': 'weighted\nintensity flow',
        'intensity_scale': 'intensity scale',
        'start_bout': 'initiating impulse',
        'scaled_impulse': 'scaled impulse',
        'position': 'pos (mm)',
        'bout_rate': 'bout rate (Hz)',
        'bout_init_speed': 'bout initial speed (mm/s)',
        'smoothed_optic_flow': 'smoothed optic flow (rad/s)',
        'smoothed_motor_drive': 'smoothed motor drive',
        'smoothed_ground_speed': 'smoothed SOG (mm/s)',
        'smoothed_swim_speed': 'smoothed swim speed (mm/s)',
        'smoothed_stimulus_speed': 'smoothed stimulus speed (mm/s)',
        'smoothed_omr_ratio': 'smoothed OMR ratio',
        'baseline_speed': 'baseline stimulus speed (mm/s)',
        'ssbf_ratio': 'swim speed to baseline flow ratio',
        'omr_ratio': 'OMR ratio',
        'swim_speed_req': 'swim speed to hold position (mm/s)',
        'baseline_flow': 'baseline optical flow (rad/s)'
    },

    'default_colours': ['C0', 'C1', 'C2', 'C3', 'C4', 'C5'],
    'default_styles': ['solid', 'dashed', 'dashdot', 'dotted'],

    'fig_path': '../figs'
}
