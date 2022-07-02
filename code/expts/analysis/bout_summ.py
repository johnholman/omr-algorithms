import numpy as np
import pandas as pd

from expts.utils.persist import load_data, save_data


def bouts_data(inpath, outpath):
    df = load_data(inpath)
    df = df[df.bout_num != -1]  # include only valid bouts
    df = df.rename(columns={"height": "height_category"})  # switch to height_category column name

    # print(df.columns)

    idx_cols = ['source', 'id', 'height_category', 'stimulus_speed', 'direction', 'seg_id', 'bout_num']
    data_cols = ['xpos', 'traj_id', 'bout_initial_speed', 'bout_peak_speed', 'bout_displacement',
                 'bout_duration',
                 'omr_bout', 'active_duration']

    agg_spec = {item: (item, 'first') for item in data_cols}
    agg_spec['end_pos'] = ('xpos', 'last')
    bouts_df = df[idx_cols + data_cols].groupby(idx_cols).agg(**agg_spec).reset_index()
    print(f'total bouts: {len(bouts_df)}')

    # calculated signed displacement - positive if in same direction as the stimulus
    sdisp = bouts_df.end_pos - bouts_df.xpos
    sdisp[bouts_df.direction == 'B'] *= -1

    # note whether start of bout occurred after goal reached
    group_cols = ['source', 'id', 'height_category', 'stimulus_speed', 'direction']
    # finished = bouts_df.groupby(group_cols)['direction', 'xpos'].apply(trial_finished)
    finished = bouts_df.groupby(group_cols).apply(trial_finished).reset_index(drop=True)

    # calculate baseline flow from mean height for the height category and stimulus speed
    hmap = {'h1': 8, 'h4': 32, 'h7': 56}
    bf = bouts_df.stimulus_speed / bouts_df.height_category.map(hmap)

    # add new columns to data
    bouts_df = bouts_df.assign(signed_displacement=sdisp, baseline_flow=bf, finished=finished)

    save_data(bouts_df, outpath)
    return bouts_df


def trial_finished(gdf):
    if gdf.iloc[0]['direction'] == 'F':
        finish = gdf.xpos > 320
    else:
        finish = gdf.xpos < 50

    after = finish[finish]

    if len(after) > 0:
        index = after.index[0]
        finish.loc[index:] = True

    return pd.Series(finish)


def summarise_bouts(bouts_file, bouts_sess_summ_file, bouts_group_summ_file):
    bdf = load_data(bouts_file)

    # calculate percentages of backward bouts for each traverse
    group_cols = ['source', 'id', 'height_category', 'stimulus_speed', 'baseline_flow', 'direction']
    btdf = bdf.groupby(group_cols, dropna=False)[['signed_displacement', 'finished']].apply(
        bouts_traverse_summary).reset_index()

    # average over traverses to get session level summary
    sessdf = btdf.groupby(['source', 'id', 'height_category', 'stimulus_speed'])[
        ['baseline_flow', 'forward']].mean().reset_index()

    save_data(sessdf, bouts_sess_summ_file)

    # summarise data for each experimental condition
    groupcols = ['source', 'height_category', 'stimulus_speed', 'baseline_flow']
    others = [item for item in sessdf.columns if item not in groupcols and item != 'id']
    spec = {}
    for item in others:
        spec[item] = (item, 'mean')
        spec[item + '_sem'] = (item, 'sem')
    print(f'{spec=}')

    gdf = sessdf.groupby(groupcols, observed=True, dropna=False).agg(**spec).reset_index()

    print(f'group df:\n{gdf.head(30)}')

    save_data(gdf, bouts_group_summ_file)

    return sessdf, gdf


def bouts_traverse_summary(gdf):
    total = sum(~gdf.finished)
    if total > 0:
        forward = sum((gdf.signed_displacement >= 0) & ~ gdf.finished) / sum(~ gdf.finished)
    else:
        forward = np.nan
    s = pd.Series(forward, index=['forward'])
    return s


if __name__ == '__main__':
    def test():
        inpath = "../data/expt/all/bouts_ts.feather"
        bouts_file = "../data/expt/all/bouts_summ.feather"
        bdf = bouts_data(inpath, bouts_file)
        bouts_sess_summ_file = "../data/expt/all/bouts_sess_summ.csv"
        bouts_group_summ_file = "../data/expt/all/bouts_group_summ.csv"
        sess_df, group_df = summarise_bouts(bouts_file, bouts_sess_summ_file, bouts_group_summ_file)


    test()
