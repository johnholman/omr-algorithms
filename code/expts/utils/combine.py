import os

import pandas as pd

from expts.utils.persist import load_data, save_data


def combine(inpaths, source_ids, outpath):
    """Combine data from multiple experiments

    :param inpaths: sequence of source data pathnames
    :param source_ids: corresponding sequence of identifiers for the data sources
    :param outpath: path for saving combined data
    """
    dfs = [load_data(inpath).assign(source=source_id) for inpath, source_id in zip(inpaths, source_ids)]
    df = pd.concat(dfs).reset_index(drop=True)
    save_data(df, outpath)

def combine_multi(fnames, indirs, source_ids, outdir):
    """Combine data files from multiple experiments

    :param fnames: filenames for data to be combined
    :param indirs: sequence of source data folders for each experiment
    :param source_ids: corresponding sequence of identifiers for the data sources
    :param outdir: folder for saving combined data
    """
    for fname in fnames:
        dfs = []
        for dir, source_id in zip(indirs, source_ids):
            inpath = os.path.join(dir, fname)
            dfs.append(load_data(inpath).assign(source=source_id))
        df = pd.concat(dfs).reset_index(drop=True)
        outpath = os.path.join(outdir, fname)
        save_data(df, outpath)
