:: process experimental data
python -m expts.process_omr_data

:: generate synthetic data for each model and procedure using the best parameters from model fitting
python -m scripts.sim.li_single_o_sbo
python -m scripts.sim.li_single_b_sbo
python -m scripts.sim.li_single_o_ribo
python -m scripts.sim.li_single_b_ribo

python -m scripts.sim.li_emp_o_rbo
python -m scripts.sim.li_emp_b_rbo
python -m scripts.sim.limi_emp_o_rbo
python -m scripts.sim.limi_emp_b_rbo

python -m scripts.sim.pmi_li_o_ribo
python -m scripts.sim.pmi_li_b_ribo
python -m scripts.sim.pmi_fbli_o_ribo
python -m scripts.sim.pmi_fbli_b_ribo
python -m scripts.sim.pmi_fli_o_ribo
python -m scripts.sim.pmi_fli_b_ribo

:: generate figures for publication
python -m figs.gen_figs



