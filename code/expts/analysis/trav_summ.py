import numpy as np
import pandas as pd

from expts.utils.persist import load_data, save_data


def summarise_traverses(df):
    # select OMR trajectory timesteps
    df = df[(~df.prune) & (df.traj_id != -1) & (df.direction != 'N')]

    # create summary table at trajectory level
    trajsumm_df = df.groupby(['id', 'height', 'stimulus_speed', 'direction', 'seg_id', 'traj_id'],
                             sort=False).apply(traj_summary).reset_index()

    # sum
    df = trajsumm_df[
        ['id', 'height', 'stimulus_speed', 'group_id', 'direction', 'duration', 'displacement', 'num_bouts',
         'total_bis']]
    tvdf = df.groupby(['id', 'height', 'stimulus_speed', 'group_id', 'direction']).sum().reset_index()

    swim_speed = tvdf.displacement / tvdf.duration
    bout_rate = tvdf.num_bouts / tvdf.duration
    bout_dist = (tvdf.displacement / tvdf.num_bouts).replace(np.inf, np.nan)
    bout_init_speed = (tvdf.total_bis / tvdf.num_bouts).replace(np.inf, np.nan)
    tvdf = tvdf.drop(columns=['total_bis'])
    tvdf = tvdf.assign(swim_speed=swim_speed, bout_rate=bout_rate, bout_dist=bout_dist, bout_init_speed=bout_init_speed)

    # only include traverses with at least one OMR-consistent bout
    tvdf = tvdf[tvdf.num_bouts != 0]

    return tvdf


def traj_summary(traj_df):
    first = traj_df.iloc[0]
    last = traj_df.iloc[-1]

    duration = (last.time - first.time).total_seconds()

    displacement = last.xpos - first.xpos if first.direction == 'F' else first.xpos - last.xpos

    # count valid OMR bouts and compute sum of their initial speeds
    boutgps = traj_df[traj_df.omr_bout & (traj_df.bout_num != -1)].groupby(['bout_num'])
    num_bouts = len(boutgps)
    total_initial_speed = boutgps.bout_initial_speed.first().sum()

    # add group identifier
    group_id = f'{first.height}_{first.stimulus_speed:.2f}'

    return pd.Series(
        {'group_id': group_id, 'duration': duration, 'displacement': displacement, 'num_bouts': num_bouts,
         'total_bis': total_initial_speed})


if __name__ == '__main__':
    def test():
        infile = r'~\data\ezfish\analysis\exp10_omr\full.feather'
        outfile = r'~\data\ezfish\analysis\exp10_omr\trav_summ_test.csv'

        pd.set_option('display.precision', 3)
        pd.set_option('display.expand_frame_repr', False)
        pd.options.display.max_rows = 200

        df = load_data(infile)

        summ_df = summarise_traverses(df)
        print(summ_df)

        save_data(summ_df, outfile, float_format='%g')

        return summ_df


    test()
