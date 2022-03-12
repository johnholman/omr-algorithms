import pandas as pd
import matplotlib.pyplot as plt

from expts.utils.persist import save_data, load_data

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.float_format', '{:.5f}'.format)


def calc_profile(df):
    """Return intensity profile dataframe for the given data based on swim speeds without normalisation at bout level

    The profile speed for each time offset from the start of a bout is calculated for the first 100 timesteps as
    the mean of the swim speeds at that offset, and then the profile normalised by dividing by the mean of the values
    for each offset.
    """

    period = 100

    # select time steps for valid bouts i.e. up to 100 timesteps
    bouts = df.loc[(df.step_num >= 0) & (df.step_num < period)]
    # find the mean normalised speed for each step number
    p = bouts[['step_num', 'swim_speed']].groupby('step_num').mean()
    p = p / p.mean()

    return p


def plot_profile(df, ax):
    """Plot the bout intensity profile for the given data

    The simple method is used to calculate the profile
    """
    p = calc_profile(df)['swim_speed']
    ax.plot(range(0, 1000, 10), p)
    ax.set_xlabel('time after bout start (ms)')
    ax.set_ylabel('relative speed')

    # calculate time to peak speed
    dt = 0.01
    peak_time = p.argmax() * dt
    peak_speed = p.max()
    rel_speed_250 = p[int(0.25 / dt)] / peak_speed
    print(f'peak time: {peak_time:.4f}  peak speed: {peak_speed:.2f} speed at 250ms rel to peak: {rel_speed_250:.3f}')


def plot_quartile_profiles(df, ax, column):
    """Plot intensity profiles for the given data using the given access.

    The data is partitioned based on the quartile values for the given column and the profile
    calculated and displayed for each partition
    """
    bouts = df.groupby(['source', 'id', 'height', 'stimulus_speed', 'direction', 'seg_id', 'bout_num'])

    values = bouts.first()[column]

    q1, q2, q3 = values.quantile(q=(0.25, 0.5, 0.75))

    print(f'{column} quantiles: {q1} {q2} {q3}')

    df1 = df[df[column] <= q1]
    p1 = calc_profile(df1)

    df2 = df[(df[column] > q1) & (df[column] <= q2)]
    p2 = calc_profile(df2)

    df3 = df[(df[column] > q2) & (df[column] <= q3)]
    p3 = calc_profile(df3)

    df4 = df[df[column] > q3]
    p4 = calc_profile(df4)

    ax.plot(range(0, 1000, 10), p1, label=f'{column} <= {q1:.2f}')
    ax.plot(range(0, 1000, 10), p2, label=f'{column} in ({q1:.2f}, {q2:.2f}]')
    ax.plot(range(0, 1000, 10), p3, label=f'{column} in ({q2:.2f}, {q3:.2f}]')
    ax.plot(range(0, 1000, 10), p4, label=f'{column} > {q3:.2f}')
    ax.legend()
    ax.set_xlabel('time after bout start (ms)')
    ax.set_ylabel('relative speed')


def calc_profiles(*, infile, allfile, omrfile):
    """Calculate and save intensity profiles from the given data

    Profiles are calculated for all bouts and for OMR bouts only
    """
    df = load_data(infile)
    all_profile = calc_profile(df)
    save_data(all_profile, allfile, float_format='%g')
    print("profile for all bouts")
    print(all_profile.swim_speed.tolist())

    omr_profile = calc_profile(df[df.omr_bout])
    save_data(omr_profile, omrfile, float_format='%g')
    print("profile for OMR bouts")
    print(omr_profile.swim_speed.tolist())


def profile_rpt(df):
    """Generate profile figures from the combined data

    Each figure shows overall profiles and separate profiles for data partitioned on the quartiles for
    either initial bout speed, bout displacement or peak bout speed, with all bouts and OMR bouts shown separately
    """
    # include only timesteps in bouts
    df = df[df.bout_num != -1]

    for prop in ['bout_initial_speed', 'bout_displacement', 'bout_peak_speed']:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 10))

        plot_profile(df, ax1)
        ax1.set_title('intensity profile for all bouts')

        plot_profile(df[df.omr_bout], ax2)
        ax2.set_title('intensity profile for OMR bouts')

        plot_quartile_profiles(df, ax3, prop)
        ax3.set_title('quartile profiles for all bouts')

        plot_quartile_profiles(df[df.omr_bout], ax4, prop)
        ax4.set_title('quartile profiles for OMR bouts')

        fig.tight_layout()


if __name__ == '__main__':
    def run():
        # calculate intensity profiles from the combined experimental data and show profile figures
        infile = '~/data/ezfish/analysis/common/full.feather'

        allfile = '~/data/ezfish/analysis/common/all_profile.csv'
        omrfile = '~/data/ezfish/analysis/common/omr_profile.csv'

        calc_profiles(infile=infile, omrfile=omrfile, allfile=allfile)

        df = load_data(infile)
        profile_rpt(df)

        print('finished')

        plt.show()


    run()
