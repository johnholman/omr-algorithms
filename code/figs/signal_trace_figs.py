# from analysis.report import report_indiv, report_groups

import matplotlib.pyplot as plt
from matplotlib import transforms

from figs.utils import create_figure
from simulator.sessrun.util import load_data


def signal_fig(*, fig_name=None, expt_name=None, proj_name=None, group_id=None, subj_id=1, start_time=0, end_time=-1,
               event_times=None, event_colors=None, event_styles=None, event_letters=None, dep_vars=None, **kwargs):
    print(f'generating {fig_name}')

    # extract records for required individual session and period
    md, df = load_data(expt_name=expt_name, project_name=proj_name)
    df = df[(df['group_id'] == group_id) & (df['subj_id'] == subj_id)]
    df = df[(df.time >= start_time) & (df.time <= end_time)]

    # add poisson rate derived variable by rectifying the start rate
    if 'poisson_rate' in dep_vars:
        df = df.assign(poisson_rate=df.start_rate.clip(lower=0))

    if 'generator_input' in dep_vars:
        df = df.assign(generator_input=df.integrated_flow.clip(lower=0))

    # add bout input generator variable by rectifying flow integrator output
    fig, axs = create_figure(len(dep_vars), nrows=len(dep_vars), fig_name=fig_name, **kwargs)
    axs = axs.flatten()

    axs[-1].set_xlabel('time (s)')
    for ax in axs[:-1]:
        hide_x_ticks_labels(ax)

    if event_times is not None:

        # create transform that maps x given in data coords for the first axes and y in axes coords to display coords
        top_ax = axs[0]
        trans = transforms.blended_transform_factory(
            top_ax.transData, top_ax.transAxes)
        # place event keys
        for time, letter in zip(event_times, event_letters):
            top_ax.text(time - 0.02, 1.1, letter, transform=trans)

    for axis_num, (ax, var_name) in enumerate(zip(axs, dep_vars)):
        # show x axis labels etc for bottom plot only
        # is_bottom = (var_name == dep_vars[-1])

        indiv_traj_plot(ax=ax, df=df, var_name=var_name, **kwargs)
        if event_times is not None:
            for event, color, style in zip(event_times, event_colors, event_styles):
                ax.axvline(event, color=color, linestyle=style)
        # if var_name in ['sensed_flow']:
        #     ax.axhline(0, color='black', linewidth=0.8)
        # ax.axhline(0, color='black', linestyle='dotted')
        # ax.axhline(0, color='black', linestyle='dotted')

    return fig


def indiv_traj_plot(*, ax, df, var_name, **_kwargs):
    default_label_map = {
        'start_rate': 'unrectified Poisson rate (Hz)',
        'poisson_rate': 'Poisson rate\n(Hz)',
        'swim_speed': 'swim speed\n(mm/s)',
        'ground_speed': 'SOG (ground_speed) (mm/s)',
        'stimulus_speed': 'stimulus speed (mm/s)',
        'integral_error': 'ierr',
        'integrated_flow': 'integrated flow',
        'generator_input': 'control\nsignal',
        'motor_output': 'motor output',
        'optic_flow': 'optic flow\n(rad/s)',
        'sensed_flow': 'sensed flow\n(rad/s)',
        'f_rate': 'flow facilitation',
        'm_rate': 'motor inhibition',
        'intensity_flow': 'weighted\nintensity flow',
        'intensity_scale': 'intensity scale',
        'scaled_impulse': 'scaled\n  impulse',
        'position': 'pos (mm)',
        'bout_rate': 'bout rate (Hz)',
        'bout_init_speed': 'bout initial speed (mm/s)',
        'baseline_speed': 'baseline stimulus speed (mm/s)',
        'ssbf_ratio': 'swim speed to baseline flow ratio',
        'omr_ratio': 'OMR ratio',
        'swim_speed_req': 'swim speed to hold position (mm/s)',
        'baseline_flow': 'baseline flow (rad/s)'
    }
    # default_label_map = {
    #     'start_rate': 'unrectified Poisson rate (Hz)',
    #     'poisson_rate': 'Poisson rate\n(Hz)',
    #     'swim_speed': 'swim speed\n(mm/s)',
    #     'ground_speed': 'SOG (ground_speed) (mm/s)',
    #     'stimulus_speed': 'stimulus speed (mm/s)',
    #     'integral_error': 'ierr',
    #     'integrated_flow': 'integrated flow',
    #     'generator_input': 'bout generator\ninput',
    #     'motor_output': 'motor output',
    #     'optic_flow': 'flow (rad/s)',
    #     'sensed_flow': 'sensed flow\n(rad/s)',
    #     'f_rate': 'flow facilitation',
    #     'm_rate': 'motor inhibition',
    #     'intensity_flow': 'weighted\nintensity flow',
    #     'intensity_scale': 'intensity scale',
    #     'scaled_impulse': 'scaled\n  impulse',
    #     'position': 'pos (mm)',
    #     'bout_rate': 'bout rate (Hz)',
    #     'bout_init_speed': 'bout initial speed (mm/s)',
    #     'baseline_speed': 'baseline stimulus speed (mm/s)',
    #     'ssbf_ratio': 'swim speed to baseline flow ratio',
    #     'omr_ratio': 'OMR ratio',
    #     'swim_speed_req': 'swim speed to hold position (mm/s)',
    #     'baseline_flow': 'baseline flow (rad/s)'
    # }

    ax.plot(df['time'], df[var_name])

    y_label = default_label_map.get(var_name, var_name)

    ax.set_ylabel(y_label)

    # if is_bottom:
    #     ax.set_xlabel('time (s)')
    # else:
    #     hide_x_ticks_labels(ax)


def hide_x_ticks_labels(ax):
    # suppress y axis ticks etc - this assumes association of dependent var with y axis!
    ax.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        labelbottom=False)  # tick labels along the bottom edge are off
    ax.set_xlabel(None)


if __name__ == '__main__':
    def test():
        # proj = 'pub21'
        group_id = '8'
        expt = 'pmi_fli_o_ribo_plus'
        dep_vars = ['optic_flow', 'sensed_flow', 'poisson_rate', 'scaled_impulse', 'swim_speed']
        start_time = 25
        end_time = 27
        signal_fig(expt_name=expt, dep_vars=dep_vars, group_id=group_id, start_time=start_time, end_time=end_time)


    test()
    plt.show()
