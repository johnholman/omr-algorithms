"""Functions to persist session data."""
# import datetime
import json
import os

import numpy as np
import pandas as pd

base_data_folder = ""
"""Base folder for data."""

METAFNAME = 'meta.json'  # filename for session metadata
DEFAULT_DATA = '_data'
csv_ext = '.csv'
feather_ext = '.feather'
np_ext = '.npy'


def set_base(base_folder):
    """Set base data folder.
    
    Args:
        base_folder: Pathname of the base folder.
    
    Results from individual runs are stored in sub-folders of
    this folder
    """
    global base_data_folder
    if len(base_folder) == 0:
        raise ValueError('base folder required')
    base_folder = os.path.normpath(os.path.expanduser(base_folder))
    if not (os.path.isabs(base_folder) and os.path.isdir(base_folder)):
        raise ValueError('base folder must be absolute path for an existing directory')

    base_data_folder = base_folder


def retrieve_data(path, *, csvargs=None):
    """Return data for the given file or directory path
    
    Args:
        path: absolute or relative path
        csvargs: additional arguments for Pandas read_csv()
        
    Returns:
        Primary data and metadata if path is a directory path
        Data loaded from path if path is a file path

        Metadata is returned as a JSON-compatible object generated from the meta.json file.

        Data stored as .csv or .feather files are returned as Pandas objects.
        Data stored as .npy files are returned as numpy arrays.

    A relative path is made absolute by prepending the base folder
    """

    if csvargs is None:
        csvargs = {}

    assert len(path) > 0
    path = os.path.normpath(os.path.expanduser(path))
    if not os.path.isabs(path):
        path = os.path.join(base_data_folder, path)

    if os.path.isdir(path):
        with open(os.path.join(path, METAFNAME)) as jfile:
            metadata = json.load(jfile)

        primary_data = load_best_format(os.path.join(path, DEFAULT_DATA), csvargs)

        data = metadata, primary_data

    else:
        data = load_best_format(path, csvargs)

    return data


def load_best_format(fpath, csvargs):
    if os.path.isfile(fname := fpath + feather_ext):
        data = pd.read_feather(fname)
    elif os.path.isfile(fname := fpath + csv_ext):
        data = pd.read_csv(fname, **csvargs)
    elif os.path.isfile(fname := fpath + np_ext):
        data = np.load(fname)
    else:
        raise Exception(f'data path {fpath} not found')
    print(f'data loaded from {fname}')
    return data


def store_data(path, data, metadata=None, *, format=None, float_format=None):
    """
    Save data to the data store.
    
    Args:
        path: folder path if saving with metadata, otherwise data file path
        metadata: JSON-compatible object to be saved as metadata.
        data:
            DataFrames are saved as Apache Arrow feather v2 or CSV files and numpy arrays as numpy .npy files.
            Filenames taken from the directory keys.
        format: format for saving Pandas dataframes - either 'feather' or 'csv'
        float_format: floating point format for CSV files (default: full precision)

    A relative path is made absolute by prepending the base folder
    """
    assert len(path) > 0
    path = os.path.normpath(os.path.expanduser(path))
    if not os.path.isabs(path):
        path = os.path.join(base_data_folder, path)

    if metadata is not None:    # save data and metadata in given folder path
        # create a new folder (including base folder) if necessary
        if not os.path.isdir(path):
            os.makedirs(path)
            print(f"created new data folder {path}")
        # save metadata in a JSON file
        with open(os.path.join(path, METAFNAME), 'w') as f:
            json.dump(metadata, f, indent=4, sort_keys=False)
        # add default datafile name to path
        path = os.path.join(path, DEFAULT_DATA)
    else:   # save data in given file path
        # create folder if necessary
        folder, filename = os.path.split(path)
        if not os.path.isdir(folder):
            os.makedirs(folder)

    # use feather as the default format
    if format is None:
        format = 'feather'

    if isinstance(data, pd.DataFrame):
        if format == 'csv':
            fname = path + csv_ext
            data.to_csv(fname, index=False, float_format=float_format)
        elif format == 'feather':
            # print(f'saving data to {path}.feather')
            fname = path + feather_ext
            data.to_feather(fname)
        else:
            raise ValueError(f'unrecognized format {format}')
    elif isinstance(data, np.ndarray):
        fname = path + np_ext
        np.save(fname, data)
    else:
        raise ValueError(f'cannot save data of type {type(data).__name__}')
    print(f'saved data to {fname}')


if __name__ == "__main__":
    # Test script only below here

    def test():

        name = r'cabbage\persist_test'
        name1 = name + '1'
        name2 = name + '2'
        name3 = name + '3'
        name4 = name + '4'

        base = r'~/temp/data/persist'
        base = os.path.normpath(os.path.expanduser(base))
        print(f'{base=}')

        set_base(base)

        md = {'name': 'john', 'age': 52}
        arr = np.array([1, 2, 3])
        df = pd.DataFrame([[1, 2, 3], [3, 2, 1]], columns=['a', 'b', 'c'])

        store_data(name1, df, md)

        store_data(name2, arr, md)

        try:
            store_data(name3, "hello", md)
        except Exception as exc:
            print(exc)

        md, newdata = retrieve_data(name1)

        print(f'metadata: {md}')
        print(newdata)

        # same thing but with default key and in CSV format
        df = pd.DataFrame([[1, 2, 3], [3, 2, 1]], columns=['a', 'b', 'z'])

        store_data(name4, df, md, format='csv')

        md, _ = retrieve_data(name4)

        print(f'metadata: {md}')
        print(f'{type(df).__name__}\n{df}')

        # save and load individual file
        df = pd.DataFrame([[1, 2, 3], [3, 2, 1]], columns=['a', 'b', 'z'])
        fname = os.path.join(name4, 'foo')
        store_data(os.path.join(name4, 'foo'), df)
        df_out = retrieve_data(fname)
        assert df.equals(df_out)
        print(fname)


    test()
