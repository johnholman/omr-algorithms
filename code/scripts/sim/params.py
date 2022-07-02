from simulator.sessrun.fit import fitted_parameters

s = ['swim_speed']
b = ['bout_rate', 'bout_init_speed']
r = ['bout_rate']

expts = {
    'li_single_sbo_fit': s,
    'li_single_ribo_fit': b,
    'li_emp_rbo_fit': r,
    'limi_emp_rbo_fit': r,
    'pmi_li_ribo_fit': b,
    'pmi_fbli_ribo_fit': b,
    'pmi_fli_ribo_fit': b,
}


expt_name = 'li_single_sbo_fit'
parms = fitted_parameters(s, expt_name=expt_name)
print()

# print(f'Running with parameters {parms} from {expt_name} costed by {features}')
#
# expt_name = 'pmi_li_ribo_fit'
# features = ['bout_rate', 'bout_init_speed']
#
# parms = fitted_parameters(features, expt_name=expt_name)
# print(f'Running with parameters {parms} from {expt_name} costed by {features}')
#
# expt_name = 'pmi_fli_ribo_fit'
# features = ['bout_rate', 'bout_init_speed']
#
# parms = fitted_parameters(features, expt_name=expt_name)
# print(f'Running with parameters {parms} from {expt_name} costed by {features}')
#
# expt_name = 'pmi_fbli_ribo_fit'
# features = ['bout_rate', 'bout_init_speed']

for expt_name, features in expts.items():
    parms = fitted_parameters(features, expt_name=expt_name)
    print(f"{expt_name} on {features}")
    for parm, value in parms.items():
        print(f"{parm}  {value:0.6f}")
    print()


