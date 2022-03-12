from matplotlib import pyplot as plt

from expts.utils.persist import load_data, save_data


def summarise_groups(session_summ_file, group_summ_file, summary_plots=False):
    """Return and save group-level summary data from given session-level summary data

    Plots are created if requested
    """
    sessdf = load_data(session_summ_file)

    # standardise column names here, for now
    sessdf = sessdf.rename(columns={"height": "height_category"})
    print(sessdf.head())

    # summarise data for each experimental condition
    groupcols = ['height_category', 'stimulus_speed', 'group_id', 'mean_height', 'baseline_flow']
    others = [item for item in sessdf.columns if item not in groupcols and item != 'id']
    spec = {}
    for item in others:
        spec[item] = (item, 'mean')
        spec[item + '_sem'] = (item, 'sem')
    print(f'{spec=}')

    gdf = sessdf.groupby(groupcols, observed=True).agg(**spec).reset_index()

    print(f'group df:\n{gdf.head(30)}')

    save_data(gdf, group_summ_file)

    # plot group means if required
    if summary_plots:
        plot_figs(gdf, group_summ_file)
        plot_bouts(gdf, group_summ_file)

    return gdf


def plot_figs(sdf, title):
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    plot_lines(axes[0][0], sdf, 'swim_speed', 'swim speed (mm/s)', 'stimulus_speed', 'stimulus speed (mm/s)')
    plot_lines(axes[0][1], sdf, 'omr_ratio', 'OMR ratio', 'stimulus_speed', 'stimulus speed (mm/s)')
    # plot_lines(axes[0][2], sdf, 'ssbf_ratio', 'SSBF ratio', 'baseline_flow', 'baseline flow (rad/s)')
    plot_lines(axes[1][0], sdf, 'bout_rate', 'bout rate (Hz)', 'stimulus_speed', 'stimulus speed (mm/s)')
    plot_lines(axes[1][1], sdf, 'bout_dist', 'bout distance (mm)', 'stimulus_speed', 'stimulus speed (mm/s)')
    plot_lines(axes[1][2], sdf, 'bout_init_speed', 'initial bout speed (mm/s)', 'stimulus_speed',
               'stimulus speed (mm/s)')
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.text(0.1, 0.97, title, fontsize='large')

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    plot_lines(axes[0][0], sdf, 'swim_speed', 'swim speed (mm/s)', 'baseline_flow', 'baseline flow (rad/s)')
    plot_lines(axes[0][1], sdf, 'ssbf_ratio', 'SSBF ratio', 'baseline_flow', 'baseline flow (rad/s)')
    # plot_lines(axes[0][1], sdf, 'omr_ratio', 'OMR ratio', 'stimulus_speed', 'stimulus speed (mm/s)')
    plot_lines(axes[1][0], sdf, 'bout_rate', 'bout rate (Hz)', 'baseline_flow', 'baseline flow (rad/s)')
    plot_lines(axes[1][1], sdf, 'bout_dist', 'bout distance (mm)', 'baseline_flow', 'baseline flow (rad/s)')
    plot_lines(axes[1][2], sdf, 'bout_init_speed', 'initial bout speed (mm/s)', 'baseline_flow',
               'baseline flow (rad/s)')

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.text(0.1, 0.97, title, fontsize='large')


def plot_bouts(sdf, title):
    if "b_dist" not in sdf.columns:
        return
    fig, axes = plt.subplots(3, 3, figsize=(9, 9))

    plot_lines(axes[0][0], sdf, 'swim_speed', 'swim speed')
    plot_lines(axes[1][0], sdf, 'ib_dur', 'interbout duration')
    plot_lines(axes[0][1], sdf, 'b_dist', 'bout distance')
    plot_lines(axes[1][1], sdf, 'b_dur', 'bout duration')
    plot_lines(axes[2][1], sdf, 'b_speed', 'bout speed')

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.text(0.1, 0.97, title, fontsize='large')


def plot_lines(ax, sdf, depvar, depvar_label, indepvar='stimulus_speed', indepvar_label='stimulus speed'):
    """ Plot curve for each height of given dependent variable against stimulus speed
    """
    for h, ldf in sdf.groupby(['height_category']):
        ax.errorbar(ldf[indepvar], ldf[depvar], yerr=ldf[depvar + '_sem'], label=h, marker='.')
    ax.set_xlabel(indepvar_label)
    ax.set_ylabel(depvar_label)
    ax.legend()
    ax.grid()


if __name__ == '__main__':
    def test():
        dirpath = r'~/data/ezfish/analysis/exp10_omr/'
        sessf = dirpath + 'session.csv'
        groupsummf = dirpath + 'group_summ_test.csv'

        summarise_groups(session_summ_file=sessf, group_summ_file=groupsummf, summary_plots=True)
        plt.show()


    test()
