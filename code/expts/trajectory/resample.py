"""
Created on 28 Jan 2020

@author: john
"""
import os

import matplotlib.pyplot as plt
import pandas as pd


def load_track_data(dirpath, fname):
    """Return tracked data for given directory and filename
    """
    path = os.path.join(os.path.expanduser(dirpath), fname)
    print(f'reading tracking data from {path}')
    _, ext = os.path.splitext(path)
    if ext == '.csv':
        df = pd.read_csv(path)
    elif ext == '.feather':
        df = pd.read_feather(path)
    else:
        raise ValueError(f'unrecognized extension {ext}')

    return df


def resample(df):
    """
    Return data resampled within sessions at 10ms intervals.

    Data values are interpolated linearly with linear extrapolation for up to 60ms to cover short
    periods of missing data. The original time column is dropped.
    """
    # rdf = df.groupby(['id', 'height', 'stimulus_speed'], sort=False).apply(resample_session)
    rdf = df.groupby(['id', 'height', 'stimulus_speed'], sort=True).apply(resample_session)
    rdf = rdf.reset_index()
    print(rdf.head(3))
    return rdf


def resample_session(df):
    """Return resampled data for a single session
    """
    print(f'resampling {df.name}')
    df = df.set_index(pd.to_timedelta(df['time'], unit='ms'))
    df = df.drop(columns=['time'])
    df = df.rename_axis('time')
    dfr = df.resample('10ms').first().interpolate(method='time', limit=6)[['xpos', 'ypos']]
    print(f'resampling output\n{dfr.head(2)}')
    return dfr


def rescale(df):
    """
    Return data with x and y position rescaled from pixels to mm
    """
    scale_factor = 0.192708
    df = df.assign(xpos=df.xpos * scale_factor, ypos=df.ypos * scale_factor)
    return df


def plot_data(tdf, rdf):
    fig, ax = plt.subplots()
    # convert tracked data time from ms to s
    tdf['time'] /= 1000
    # converted resampled data times from Timedelta to s as float
    rdf['time'] = pd.to_numeric(rdf['time']) / 1000000000

    ax.plot(tdf['time'], tdf['xpos'], 'o')
    ax.plot(rdf['time'], rdf['xpos'], '.')
    ax.set_ylim((0, 380))
