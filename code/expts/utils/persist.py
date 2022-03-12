import os
import pandas as pd

def load_data(path, typespec=None):
    """Return DataFrame for given file path

    CSV and feather formats are supported and selected by file extension
    If a time column is present it is assumed to contain nanosecond data and is converted
    to a timedelta
    """
    path = os.path.expanduser(path)
    print(f'loading from {path}')
    _, ext = os.path.splitext(path)
    if ext == '.csv':
        df = pd.read_csv(path, dtype=typespec)
    elif ext == '.feather':
        df = pd.read_feather(path)
    else:
        raise ValueError(f'unrecognized extension {ext}')

    if 'time' in df.columns:
        df['time'] = pd.TimedeltaIndex(df['time'], unit='nano')

    return df


def save_data(df, path, float_format=None):
    """Save data to given directory and filename

    Any column labelled "time" is assumed to contain timedelta data and
    is converted to nanoseconds
    """
    _, ext = os.path.splitext(path)
    path = os.path.expanduser(path)
    print(f'saving to {path}')
    # print(f'saving to {path} as {ext}:\n{df.head(2)}')

    # convert timedelta to integer
    if 'time' in df.columns:
        df = df.assign(time=pd.to_numeric(df['time']))

    if ext == '.csv':
        if float_format is None:
            float_format = '%.8f'
        df.to_csv(path, index=False, float_format=float_format)
    elif ext == '.feather':
        df = df.reset_index(drop=True)
        df.to_feather(path)
    else:
        raise ValueError(f'unrecognized extension {ext}')
