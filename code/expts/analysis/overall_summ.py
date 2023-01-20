import pandas as pd

from expts.utils.persist import load_data, save_data


def summarise_traverses_overall(df):
    """
    Summarise timestep-level data at traverse level to compute overall displacement and duration
    :param df:
    :return:
    """
    # select timesteps that occur when the stimulus is moving with position data available
    df = df[(df.seg_id != -1) & (df.direction != 'N') & ~df.reached_goal]

    df = df[
        ['id', 'height', 'stimulus_speed', 'direction', 'time', 'xpos']]
    tvdf = df.groupby(['id', 'height', 'stimulus_speed', 'direction']).apply(trav_summary).reset_index()
    return tvdf


def trav_summary(tdf):
    first = tdf.iloc[0, :]
    last = tdf.iloc[-1, :]

    # calculate total displacement in direction of stimulus
    disp = last.xpos - first.xpos
    if first['direction'] == 'B':
        disp = -disp

    # calculate total duration and mean speed in direction of stimulus
    duration = (last.time - first.time).total_seconds()
    speed = disp / duration

    summ = pd.Series({'total_displacement': disp, 'total_duration': duration, 'overall_speed': speed})
    return summ


def add_overall_data(omr_df, summ_df):
    """
    Add overall fields to the summary of OMR behaviour at traverse level
    :param omr_df:
    :param summ_df:
    :return:
    """
    summ_df = omr_df.merge(summ_df, on=['id', 'stimulus_speed', 'direction', 'height'], how='left', sort=False)
    return summ_df


if __name__ == '__main__':
    def test():
        infname = "../data/expt/or/bouts_ts.feather"
        outfname = "../data/expt/or/overall_summ.csv"
        outfullfname = "../data/expt/or/overall_full_summ.csv"

        omrsummfname = "../data/expt/or/trav_summ.csv"

        pd.set_option('display.precision', 3)
        pd.set_option('display.expand_frame_repr', False)
        pd.options.display.max_rows = 200

        df = load_data(infname)
        omr_df = load_data(omrsummfname)

        summ_df = summarise_traverses_overall(df)
        print(summ_df)

        save_data(summ_df, outfullfname, float_format='%g')

        summ_df = add_overall_data(omr_df, summ_df)
        save_data(summ_df, outfname, float_format='%g')

        return summ_df


    test()
