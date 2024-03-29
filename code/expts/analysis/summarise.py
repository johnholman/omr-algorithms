import os
from matplotlib import pyplot as plt

from expts.analysis.group_summ import summarise_groups
from expts.analysis.overall_summ import summarise_traverses_overall, add_overall_data
from expts.analysis.sess_summ import summarise_sessions
from expts.analysis.trav_summ import summarise_traverses
from expts.utils.persist import load_data, save_data


def summarise(data_folder, bouts_ts_f, session_f, group_f):
    """
    Summarise experimental data at session and group levels from timeseries data

    :param data_folder: path to data folder
    :param bouts_ts_f: filename for timeseries data including bout info
    :param session_f: filename for session-level summary
    :param group_f: filename for group-level summary
    """
    infile = os.path.join(data_folder, bouts_ts_f)
    trav_path = os.path.join(data_folder, 'trav_summ.csv')
    overall_trav_path = os.path.join(data_folder, 'overall_trav_summ.csv')
    sess_path = os.path.join(data_folder, session_f)
    csess_path = os.path.join(data_folder, 'session_complete.csv')
    group_path = os.path.join(data_folder, group_f)

    df = load_data(infile)

    summ_df = summarise_traverses(df)
    save_data(summ_df, trav_path, float_format='%g')

    overall_summ_df = summarise_traverses_overall(df)

    # save_data(summ_df, outfullfname, float_format='%g')

    summ_df = add_overall_data(summ_df, overall_summ_df)
    save_data(summ_df, overall_trav_path, float_format='%g')

    prefilter = None
    mean_heights = {'h1': 8.0, 'h4': 32.0, 'h7': 56.0}
    nrepeated = 5  # number of repeated levels, i.e. stimulus speed values
    criterion = 2

    summarise_sessions(infile=overall_trav_path, all_sessions_file=sess_path, complete_sessions_file=csess_path,
                       mean_heights=mean_heights, prefilter=prefilter, criterion=criterion, no_outliers=False,
                       nrepeated=nrepeated, distrib_plots=False)

    summarise_groups(session_summ_file=sess_path, group_summ_file=group_path, summary_plots=True)


def prune(group_summ_f, dirs, group_summ_pruned_f):
    """
    Remove outlying condition where stimulus speed is very low from group summaries in the given directories
    """
    for d in dirs:
        inpath = os.path.join(d, group_summ_f)
        outpath = os.path.join(d, group_summ_pruned_f)
        df = load_data(inpath)
        df = df[df.stimulus_speed >= 1.0]
        save_data(df, outpath)


if __name__ == '__main__':
    def test():
        data_folder = "../data/expt/or/"
        bouts_ts_f = 'bouts_ts.feather'  # filename for timeseries data including trajectory and bout info
        session_f = 'session.csv'  # filename for session-level summary
        group_f = 'group_summ.csv'  # filename for group summary

        summarise(data_folder, bouts_ts_f=bouts_ts_f, session_f=session_f, group_f=group_f)


    test()
    plt.show()
