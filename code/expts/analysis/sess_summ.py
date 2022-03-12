# Generate session-level and group-level summaries from traverse summary data

import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.dtypes.dtypes import CategoricalDtype

from expts.utils.persist import save_data, load_data


def accepted(df, criterion=None):
    nrec = len(df)
    if 'duration' in df.columns:  # j pipeline
        if criterion is None:
            criterion = 0.0
        df = df[df.duration > criterion]
    else:  # w pipeline
        if criterion is not None:
            df = df[df['cat'].isin(list(criterion))]
    print(f'number of accepted swim records {len(df)} out of {nrec}')
    return df


def prune_outliers(df):
    """Return dataframe with outliers pruned.

    Traverse records with outlying values of swim speed are removed for each combination of height
    and stimulus speed
    """
    grouped = df.groupby(['height', 'stimulus_speed'])['swim_speed']
    is_zoutlier = grouped.transform(z_outliers)
    is_qoutlier = grouped.transform(q_outliers)
    df = df[~is_qoutlier & ~is_zoutlier]
    print(f'\n{len(df)} records after pruning outliers:\n{df}')
    return df


def z_outliers(s):
    med = s.median()
    devs = s - med
    mad = devs.abs().median()
    mod_z = 0.6745 * devs / mad
    is_outlier = abs(mod_z) > 3.5
    outliers = [round(item, 2) for item in s[is_outlier]]
    print(f'z outliers {s.name}: median {med:.2f}, MAD: {mad:.2f}, {len(outliers)} outliers: {outliers}')

    return is_outlier


def q_outliers(s):
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    is_outlier = (s > q3 + iqr * 1.5) | (s < q1 - iqr * 1.5)
    outliers = [round(item, 2) for item in s[is_outlier]]

    print(f'q outliers {s.name}: q1-q3: {q1:.2f}-{q3:.2f}, iqr: {iqr:.2f}, {len(outliers)} outliers: {outliers}')

    return is_outlier


def add_derived_data(df, mean_heights):
    df = df.copy()  # avoid mutating argument

    # add mean height column
    df['mean_height'] = [mean_heights[cat] for cat in df['height']]

    # add baseline flow
    # df['baseline_flow'] = df['stimulus_speed'] / df['mean_height']
    df['baseline_flow'] = round(df['stimulus_speed'] / df['mean_height'], 5)

    # add swim speed relative to baseline flow - i.e. SSBFR
    df['ssbf_ratio'] = df['swim_speed'] / df['baseline_flow']

    # add OMR ratio
    df['omr_ratio'] = df['swim_speed'] / df['stimulus_speed']

    # add bout swim speed if bout data available
    if 'b_dist' in df.columns and 'b_dur' in df.columns:
        df['b_speed'] = df['b_dist'] / df['b_dur'] * 1000

    print(f'with derived variables:\n{df.head(10)}')

    return df


def prune_incomplete(df, nrecs):
    """Return dataframe including only subjects with valid data for all conditions experienced.

    nrecs is the number of records expected for a subject with complete data
    """
    complete_df = df.groupby('id').filter(lambda gdf: len(gdf) == nrecs)
    print(f'{len(complete_df.id.unique())} out of {len(df.id.unique())} fish have valid data for all speeds')
    return complete_df


def plot_descript(df, title_prefix):
    # histograms of swim speeds for each condition
    fig, axes = plt.subplots(3, 4, figsize=(12, 8))
    axes = [ax for axlist in axes for ax in axlist]
    groups = df.groupby(['height', 'stimulus_speed'])
    for ax, ((h, ss), dfg) in zip(axes, groups):
        ax.hist(dfg['swim_speed'], bins=6)
        ax.set_title(f'height {h} stimulus speed {ss}', fontsize='medium')
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    title = f'{title_prefix}: swim speed histograms'
    fig.text(0.1, 0.97, title, fontsize='large')

    # box plots of swim speed for each condition
    fig, axes = plt.subplots(3, 4, figsize=(12, 8))
    axes = [ax for axlist in axes for ax in axlist]
    groups = df.groupby(['height', 'stimulus_speed'])
    for ax, ((h, ss), dfg) in zip(axes, groups):
        ax.boxplot(dfg['swim_speed'])
        ax.set_title(f'height {h} stimulus speed {ss}', fontsize='medium')
        ax.set_ylim((0, 30))
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    title = f'{title_prefix}: swim speed box plots'
    fig.text(0.1, 0.97, title, fontsize='large')

    # histograms of ssbfr for each condition
    fig, axes = plt.subplots(3, 4, figsize=(12, 8))
    axes = [ax for axlist in axes for ax in axlist]
    groups = df.groupby(['height', 'stimulus_speed'])
    for ax, ((h, ss), dfg) in zip(axes, groups):
        ax.hist(dfg['ssbf_ratio'], bins=6)
        ax.set_title(f'height {h} stimulus speed {ss}', fontsize='medium')
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    title = f'{title_prefix}: histograms of swim speed to baseline flow ratio'
    fig.text(0.1, 0.97, title, fontsize='large')

    # box plots of ssbfr for each condition
    fig, axes = plt.subplots(3, 4, figsize=(12, 8))
    axes = [ax for axlist in axes for ax in axlist]
    groups = df.groupby(['height', 'stimulus_speed'])
    for ax, ((h, ss), dfg) in zip(axes, groups):
        ax.boxplot(dfg['ssbf_ratio'])
        # ax.boxplot(dfg['ssbfr'], whis='range')
        ax.set_title(f'height {h} stimulus speed {ss}', fontsize='medium')
        ax.set_ylim((0, 60))
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    title = f'{title_prefix}: box plots for swim speed to baseline flow ratio'
    fig.text(0.1, 0.97, title, fontsize='large')


# def postprocess(*, basedir, infile, mean_heights, prefilter=None, criterion=None, no_outliers=False,
#                 nrepeated=1, summary_plots=True, distrib_plots=False):
#     pd.set_option('display.precision', 3)
#     pd.set_option('display.expand_frame_repr', False)
#     # pd.set_option('display.max_rows', 100)
#
#     outfile = 'session.csv'
#     outfile2 = 'session_complete.csv'
#     groupsumm = 'group_summ.csv'
#
#     inpath = os.path.join(basedir, infile)
#     outpath = os.path.join(basedir, outfile)
#     outpath2 = os.path.join(basedir, outfile2)
#     groupsummpath = os.path.join(basedir, groupsumm)
#
#     type_spec = {'Height': CategoricalDtype(categories=mean_heights.keys(), ordered=True)}
#     df = load_data(basedir, infile, typespec=type_spec)
#
#     if prefilter is not None:
#         df = prefilter(df)
#
#     if no_outliers:
#         df = prune_outliers(df)
#
#     if criterion is not None:
#         df = accepted(df, criterion)
#
#     # take means for remaining traversals for the same subject and experimental condition
#     # observed=True prevents the unexpected behaviour of the merge step generating records for all combinations
#     # of the groupby variables when one of them is categorical
#     df = df.groupby(['height', 'stimulus_speed', 'id'], as_index=False, observed=True).mean()
#     print(f'data  - {len(df)} records\n{df.head(20)}')
#
#     df = add_derived_data(df, mean_heights)
#
#     # save all data
#     df.to_csv(outpath, index=False)
#
#     # save data only for subjects with complete data
#     complete_df = prune_incomplete(df, nrepeated)
#     complete_df.to_csv(outpath2, index=False)
#
#     # create and save group level summary
#     sdf = summarise_groups(df)
#     sdf.to_csv(groupsummpath, index=False)
#
#     # plot group means if required
#     if summary_plots:
#         plot_figs(sdf, inpath)
#         plot_bouts(sdf, inpath)
#
#     # show descriptive stats for subjects with complete data
#     if distrib_plots:
#         plot_descript(complete_df, inpath)
#
def summarise_sessions(*, infile, all_sessions_file, complete_sessions_file, mean_heights, prefilter=None,
                       criterion=None, no_outliers=False, nrepeated=1, distrib_plots=False):
    pd.set_option('display.precision', 3)
    pd.set_option('display.expand_frame_repr', False)
    # pd.set_option('display.max_rows', 100)

    # inpath = os.path.join(basedir, infile)
    # outpath = os.path.join(basedir, outfile)
    # outpath2 = os.path.join(basedir, outfile2)
    # groupsummpath = os.path.join(basedir, groupsumm)

    type_spec = {'Height': CategoricalDtype(categories=mean_heights.keys(), ordered=True)}
    df = load_data(infile, typespec=type_spec)

    if prefilter is not None:
        df = prefilter(df)

    if no_outliers:
        df = prune_outliers(df)

    if criterion is not None:
        df = accepted(df, criterion)

    # take means for remaining traversals for the same subject and experimental condition
    # observed=True prevents the unexpected behaviour of the merge step generating records for all combinations
    # of the groupby variables when one of them is categorical
    df = df.groupby(['height', 'stimulus_speed', 'group_id', 'id'], as_index=False, observed=True).mean()
    print(f'data  - {len(df)} records\n{df.head(20)}')

    df = add_derived_data(df, mean_heights)

    # save all data
    save_data(df, all_sessions_file)

    # save data only for subjects with complete data
    complete_df = prune_incomplete(df, nrepeated)
    save_data(complete_df, complete_sessions_file)

    # # create and save group level summary
    # sdf = summarise_groups(df)
    # save_data(sdf, group_summ_file)
    #
    # # plot group means if required
    # if summary_plots:
    #     plot_figs(sdf, infile)
    #     plot_bouts(sdf, infile)

    # show descriptive stats for subjects with complete data
    if distrib_plots:
        plot_descript(complete_df, infile)


if __name__ == "__main__":
    def test():
        """Process results from the final omr ratio experiment (expt 10)
        using summarised traverses from the j pipeline
        """
        dirpath = r'~/data/ezfish/analysis/exp10_omr/'
        infile = dirpath + 'trav_summ.csv'
        sessf = dirpath + 'session_test.csv'
        csessf = dirpath + 'session_complete_test.csv'

        pd.set_option('display.precision', 3)
        pd.set_option('display.expand_frame_repr', False)
        pd.options.display.max_rows = 200

        prefilter = None

        mean_heights = {'h1': 8.0, 'h4': 32.0, 'h7': 56.0}
        nrepeated = 5  # number of repeated levels, i.e. stimulus speed values
        criterion = 2

        summarise_sessions(infile=infile, all_sessions_file=sessf, complete_sessions_file=csessf,
                           mean_heights=mean_heights, prefilter=prefilter, criterion=criterion, no_outliers=False,
                           nrepeated=nrepeated, distrib_plots=True)

        plt.show()


    test()
