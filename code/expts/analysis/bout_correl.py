import numpy as np
import pandas as pd

from expts.utils.persist import load_data, save_data


def bout_correl(bouts_file: str, bouts_sess_summ_file: str, bouts_group_summ_file: str):
    """
    Summmarise bout data at session and group level

    :param bouts_file: path for bouts data file
    :param bouts_sess_summ_file: path for bouts session summary file
    :param bouts_group_summ_file: path for bouts group summary file
    :return: session and group summary dataframes
    """
    bdf = load_data(bouts_file)

    group_cols = ['source', 'id', 'height_category', 'stimulus_speed', 'baseline_flow']
    data_cols = ['bout_initial_speed', 'bout_duration', 'omr_bout']
    sessdf = bdf.groupby(group_cols, dropna=False)[data_cols].apply(
        bouts_session_correl).reset_index()

    # # average over traverses to get session level summary
    # data_cols = ['baseline_flow', 'forward', 'corr']
    # sessdf = btdf.groupby(['source', 'id', 'height_category', 'stimulus_speed'])[data_cols].mean().reset_index()
    # # sessdf = btdf.groupby(['source', 'id', 'height_category', 'stimulus_speed'])[
    # #     ['baseline_flow', 'forward']].mean().reset_index()

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


def bouts_session_correl(gdf):
    # calculate r for all bouts
    if len(gdf) >= 2:
        corr = gdf.bout_initial_speed.corr(gdf.bout_duration)
    else:
        corr = np.nan

    # calculate r for OMR bouts only under 1s in duration
    ogdf = gdf[gdf.omr_bout]
    if len(ogdf) >= 2:
        ocorr = ogdf.bout_initial_speed.corr(ogdf.bout_duration)
    else:
        ocorr = np.nan

    s = pd.Series([ocorr, corr], index=['omr_corr', 'all_corr'])
    return s


if __name__ == '__main__':
    def test():
        inpath = "../data/expt/all/bouts_ts.feather"
        bouts_file = "../data/expt/all/bouts_summ.feather"
        bouts_sess_summ_file = "../data/expt/all/bouts_sess_correl.csv"
        bouts_group_summ_file = "../data/expt/all/bouts_group_correl.csv"
        sess_df, group_df = bout_correl(bouts_file, bouts_sess_summ_file, bouts_group_summ_file)


    test()
