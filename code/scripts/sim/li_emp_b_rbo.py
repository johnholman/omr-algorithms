from simulator.analysis.report import report_comparison, indiv_rpt_expt, group_rpt_expt, summary_rpt_expt
from simulator.sessrun.erunner import run_expt
from simulator.sessrun.fit import fitted_parameters

expt_name = 'li_emp_rbo_fit'

result_id = None

description = "rate: P/LI, intensity: empirical values, BF procedure using fit to combined data on bout rate"

cfg = {
    'environment.classname': 'simulator.environment.freeswim.FreeSwimEnvironment',
    'controller.classname': 'simulator.agent.controller.DualControllerSpecifiedIntensity',
    'boutgenerator.classname': 'simulator.agent.bouts.BoutGenerator',
    'procedure': 'BF',

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

# basic OMR procedure
# vcfg = {'height': [8, 32, 56], 'stimulus_speed': [4, 6, 8, 10, 12]}

# # baseline flow procedure
# vcfg = [
#     {'height': 8, 'stimulus_speed': 0.8},
#     {'height': 8, 'stimulus_speed': 1.6},
#     {'height': 8, 'stimulus_speed': 2.4},
#     {'height': 8, 'stimulus_speed': 3.2},
#     {'height': 8, 'stimulus_speed': 4.0},
#     {'height': 32, 'stimulus_speed': 3.2},
#     {'height': 32, 'stimulus_speed': 6.4},
#     {'height': 32, 'stimulus_speed': 9.6},
#     {'height': 32, 'stimulus_speed': 12.8},
#     {'height': 32, 'stimulus_speed': 16.0},
#     {'height': 56, 'stimulus_speed': 5.6},
#     {'height': 56, 'stimulus_speed': 11.2},
#     {'height': 56, 'stimulus_speed': 16.8},
#     {'height': 56, 'stimulus_speed': 22.4},
#     {'height': 56, 'stimulus_speed': 28},
# ]

# baseline flow procedure with observed mean bout initial speeds
vcfg = [
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

features = ['bout_rate']

# get parameters and costs from the best fit result
parms = fitted_parameters(features, expt_name=expt_name, n=result_id)
print(f'Running with parameters {parms} from {expt_name} costed by {features}')

# add optimised parameters to the fixed ones given above and increased number of subjects
cfg = {**cfg, **parms}

# run the simulation with this configuration
data = _, df = run_expt(description=description, cfg=cfg, vcfg=vcfg, save=True, verbose=False)
# data = get_data()

indiv_rpt_expt(data, groups=[1, 2, 4, 7, 10, 14], period=(25, 27),
               dep_vars=['optic_flow', 'sensed_flow', 'start_rate', 'scaled_impulse', 'swim_speed', ])

indiv_rpt_expt(data, groups=[1, 2, 4, 7, 10, 14], title='20', period=-20,
               dep_vars=['optic_flow', 'sensed_flow', 'start_rate', 'scaled_impulse', 'swim_speed', ])

group_rpt_expt(data, dep_vars=['smoothed_swim_speed', 'smoothed_omr_ratio'], win_size=100)

summary_rpt_expt(data, indep_vars=['height', 'baseline_flow'],
                 dep_vars=['bout_rate', 'bout_init_speed', 'bout_rate_unfiltered', 'bout_init_speed_unfiltered',
                           'swim_speed', 'omr_ratio'],
                 period=-20, ncolumns=2,
                 title='last 20 s')

report_comparison(proc=cfg['procedure'], predicted=data,
                  indep_vars=['height_category', 'baseline_flow'],
                  dep_vars=['bout_rate', 'bout_init_speed', 'swim_speed', 'omr_ratio'],
                  ncolumns=2)

if result_id is None:
    print(f'Run with best parameters {parms} from {expt_name} costed by {features}')
else:
    print(f'Run with parameters {parms} from {expt_name} result id {result_id}')

# plt.show()
