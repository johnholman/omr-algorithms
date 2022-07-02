from matplotlib import pyplot as plt

from figs.bout_duration_figs import bout_duration_fig
from figs.compare_figs import compare_fig
from figs.error_figs import errs_fig
from figs.expt_figs import expt_fig, expt_fig_one_var
from figs.expt_figs_bout_direction import expt_fig_directionality
from figs.expt_figs_limitbf import expt_fig_limitbf
from figs.profile_figs import quartile_profile_fig, overall_profile_fig
from figs.signal_trace_figs import signal_fig
from figs.utils import save_figure


def main():
    # mm = 0.0394 # scale factor millimeteres to inches
    plt.rcParams['figure.max_open_warning'] = 50
    plt.rcParams['figure.titlesize'] = 9
    plt.rcParams['figure.constrained_layout.w_pad'] = 4 / 72
    plt.rcParams['figure.constrained_layout.h_pad'] = 4 / 72
    plt.rcParams['figure.constrained_layout.hspace'] = 0
    plt.rcParams['figure.constrained_layout.wspace'] = 0

    plt.rcParams['axes.labelsize'] = 7.5
    plt.rcParams['axes.titlesize'] = 7.5
    plt.rcParams['axes.labelpad'] = 3
    plt.rcParams['xtick.labelsize'] = 6.5
    plt.rcParams['ytick.labelsize'] = 6.5
    plt.rcParams['xtick.major.pad'] = 2
    plt.rcParams['ytick.major.pad'] = 1
    plt.rcParams['legend.fontsize'] = 7
    plt.rcParams['legend.title_fontsize'] = 7
    plt.rcParams['lines.linewidth'] = 1
    plt.rcParams['lines.markersize'] = 4

    fig_dir = '../figs'
    proj_name = 'sim'  # project name for the simulation scripts

    # formats = ['pdf', 'png', 'svg']
    formats = 'svg'
    ri = ['bout_rate', 'bout_init_speed']
    s = ['swim_speed']

    fig_name = '1E - OR expt results - swim speed & OMR ratio'
    dept_vars = ['swim_speed', 'omr_ratio']
    fig = expt_fig(procs=['OR'], dept_vars=dept_vars, fig_name=fig_name, size=(90, 50))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '1F - OR expt results - bout measures'
    dept_vars = ['bout_rate', 'bout_init_speed']
    fig = expt_fig(procs=['OR'], dept_vars=dept_vars, fig_name=fig_name, size=(90, 50))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '2B - bout duration histogram'
    fig = bout_duration_fig(size=(65, 55))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '2C - BF expt results - swim speed & OMR ratio'
    dept_vars = ['swim_speed', 'omr_ratio']
    fig = expt_fig(procs=['BF'], dept_vars=dept_vars, fig_name=fig_name, size=(90, 50),
                   ylim_map={'omr_ratio': (0, 8)})
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '2D - BF expt results - bout measures'
    dept_vars = ['bout_rate', 'bout_init_speed']
    fig = expt_fig(procs=['BF'], dept_vars=dept_vars, fig_name=fig_name, size=(90, 50),
                   ylim_map={'omr_ratio': (0, 8)})
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '2E - overall bout intensity profiles'
    fig = overall_profile_fig(fig_name=fig_name, size=(55, 55))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '2F - quartile bout intensity profiles'
    fig = quartile_profile_fig(fig_name=fig_name, size=(110, 55))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '3B - sample trace for basic model'
    group_id = '8'
    expt = 'li_single_o_ribo'
    dep_vars = ['swim_speed', 'optic_flow', 'sensed_flow', 'generator_input', 'scaled_impulse']
    event_times = [25.29, 25.51, 25.68, 25.88, 26.10, 26.27, 26.31]
    event_colors = ['red', 'red', 'red', 'green', 'green', 'green', 'magenta']
    event_styles = ['dotted', 'dashdot', 'dashed', 'dotted', 'dashdot', 'dashed', 'dotted']
    event_letters = 'abcdefg'
    start_time = 25.25
    end_time = 26.50
    fig = signal_fig(expt_name=expt, proj_name=proj_name, dep_vars=dep_vars, group_id=group_id,
                     start_time=start_time, end_time=end_time, event_times=event_times, event_colors=event_colors,
                     event_styles=event_styles, event_letters=event_letters, fig_name=fig_name, size=(100, 100))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '3D - model 1 fitted to OR on swim speed'
    expts = ['li_single_o_sbo']
    dept_vars = ['swim_speed', 'omr_ratio']
    fig = compare_fig(expts=expts, procs=['OR'], dep_vars=dept_vars, proj_name=proj_name,
                      fig_name=fig_name, vars_in_cols=False, size=(90, 60))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '3E - model 1 fitted to BF on swim speed'
    expts = ['li_single_b_sbo']
    dept_vars = ['swim_speed', 'omr_ratio']
    fig = compare_fig(expts=expts, procs=['BF'], dep_vars=dept_vars, proj_name=proj_name,
                      fig_name=fig_name, vars_in_cols=False, size=(90, 60))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '4A - prediction errors for basic model'
    expts = {'swim speed fit': ('li_single_sbo_fit', 'sim', s),
             'bout data fit': ('li_single_ribo_fit', 'sim', ri),
             }
    measurements = {
        'bout rate': 'bout_rate',
        'bout intensity': 'bout_init_speed',
        'swim speed': 'swim_speed',
    }
    fig = errs_fig(expts, measurements, fig_name=fig_name, size=(55, 55))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '4C - bout rates for basic model fitted to bout stats'
    expts = ['li_single_o_ribo', 'li_single_b_ribo']
    dept_vars = ['bout_rate']
    fig = compare_fig(expts=expts, proj_name=proj_name, procs=['OR', 'BF'], dep_vars=dept_vars, fig_name=fig_name,
                      size=(90, 60))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '4D - bout rates with improved bout generator'
    expts = ['limi_emp_o_rbo', 'limi_emp_b_rbo']
    dept_vars = ['bout_rate']
    fig = compare_fig(expts=expts, proj_name=proj_name, procs=['OR', 'BF'], dep_vars=dept_vars, fig_name=fig_name,
                      size=(90, 60))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '5A - prediction errors for model variants'
    expts = {
        'basic model': ('li_single_ribo_fit', 'sim', ri),
        'model A': ('pmi_li_ribo_fit', 'sim', ri),
        'model B': ('pmi_fbli_ribo_fit', 'sim', ri),
        'model C': ('pmi_fli_ribo_fit', 'sim', ri),
    }
    measurements = {
        'bout rate': 'bout_rate',
        'bout intensity': 'bout_init_speed',
        # 'overall bout fit': 'cost',
        'swim speed': 'swim_speed',
    }
    fig = errs_fig(expts, measurements=measurements, fig_name=fig_name, size=(70, 50))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '5B - model C compared to experimental OMR data'
    expts = ['pmi_fli_o_ribo']
    dept_vars = ['bout_rate', 'bout_init_speed', 'swim_speed']
    fig = compare_fig(expts=expts, proj_name=proj_name, procs=['OR'], dep_vars=dept_vars, fig_name=fig_name,
                      size=(55, 130))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '5C - model C compared to experimental BF data'
    expts = ['pmi_fli_b_ribo']
    dept_vars = ['bout_rate', 'bout_init_speed', 'swim_speed']
    fig = compare_fig(expts=expts, proj_name=proj_name, procs=['BF'], dep_vars=dept_vars, fig_name=fig_name,
                      size=(55, 130))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = '5D - sample trace for model C'
    group_id = '8'
    expt = 'pmi_fli_o_ribo'
    dep_vars = ['optic_flow', 'sensed_flow', 'poisson_rate', 'scaled_impulse', 'swim_speed']
    start_time = 25
    end_time = 27
    fig = signal_fig(expt_name=expt, proj_name=proj_name, dep_vars=dep_vars, group_id=group_id,
                     start_time=start_time, end_time=end_time, fig_name=fig_name, size=(60, 130))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S1A - peak speed quartile bout speed profiles'
    fig = quartile_profile_fig(fig_name=fig_name, quartile_feature='bout_peak_speed', size=(110, 60))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S1B - displacement quartile bout speed profiles'
    fig = quartile_profile_fig(fig_name=fig_name, quartile_feature='bout_displacement', size=(110, 60))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S2A - BF bout measures for moderate stimulus speeds'
    dept_vars = ['bout_rate', 'bout_init_speed']
    fig = expt_fig_limitbf(procs=['BF'], dept_vars=dept_vars, minss=3, maxss=15, fig_name=fig_name, size=(90, 50))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S2B - bout duration'
    dept_vars = ['bout_active_duration']
    fig = expt_fig_one_var(procs=['OR', 'BF'], dept_vars=dept_vars, fig_name=fig_name, size=(110, 50))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S2C - directionality index'
    dept_vars = ['forward']
    fig = expt_fig_directionality(procs=['OR', 'BF'], dept_vars=dept_vars, fig_name=fig_name, size=(120, 60))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S3A - rate-only model without motor inhibition'
    expts = ['li_emp_o_rbo', 'li_emp_b_rbo']
    dept_vars = ['bout_rate']
    fig = compare_fig(expts=expts, proj_name=proj_name, procs=['OR', 'BF'], dep_vars=dept_vars, fig_name=fig_name,
                      size=(90, 60))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S4A - model A compared to experimental OMR data'
    expts = ['pmi_li_o_ribo']
    dept_vars = ['bout_rate', 'bout_init_speed', 'swim_speed']
    fig = compare_fig(expts=expts, proj_name=proj_name, procs=['OR'], dep_vars=dept_vars, fig_name=fig_name,
                      vars_in_cols=False, size=(140, 50))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S4B - model A compared to experimental BF data'
    expts = ['pmi_li_b_ribo']
    dept_vars = ['bout_rate', 'bout_init_speed', 'swim_speed']
    fig = compare_fig(expts=expts, proj_name=proj_name, procs=['BF'], dep_vars=dept_vars, fig_name=fig_name,
                      vars_in_cols=False, size=(140, 50))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S4C - model B compared to experimental OMR data'
    expts = ['pmi_fbli_o_ribo']
    dept_vars = ['bout_rate', 'bout_init_speed', 'swim_speed']
    fig = compare_fig(expts=expts, proj_name=proj_name, procs=['OR'], dep_vars=dept_vars, fig_name=fig_name,
                      vars_in_cols=False, size=(140, 50))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    fig_name = 'S4D - model B compared to experimental BF data'
    expts = ['pmi_fbli_b_ribo']
    dept_vars = ['bout_rate', 'bout_init_speed', 'swim_speed']
    fig = compare_fig(expts=expts, proj_name=proj_name, procs=['BF'], dep_vars=dept_vars, fig_name=fig_name,
                      vars_in_cols=False, size=(140, 50))
    save_figure(fig, fig_name, fig_dir, formats=formats)

    print('finished')


if __name__ == '__main__':
    main()
    # plt.show()
