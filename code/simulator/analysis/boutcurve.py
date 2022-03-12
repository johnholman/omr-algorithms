# Plot the relationship between constant bout generator input (u) and mean of output (swim intensity)
# for the logistic poisson-initiated fixed bout generator

from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean

from simulator.sessrun.util import create_component


def iocurve(cfg, description=None, nsamples=10000, minu=-0.5, maxu=1.5, npoints=10):
    """Plot input/output curve for bout generator with constant input.

    :param cfg: bout generator configuration as dictionary
    :param description: description for plot title
    :param nsamples: number of samples for each level of drive
    :param minu: minimum input drive to plot
    :param maxu: maximum input drive to plot
    :param npoints: number of points to plot
    """
    common_cfg = cfg['common'] if 'common' in cfg else cfg

    common_cfg['rgen'] = np.random.RandomState(0)

    bg = create_component('boutgenerator.classname', **common_cfg)
    bg.configure(**common_cfg)
    print(f'plotting input/output curve for {bg}')

    drives = np.linspace(minu, maxu, npoints)
    print(f'input drives {drives}, num samples per point {nsamples}')
    m = [mean(bg.select_action(drive) for _ in range(nsamples)) for drive in drives]

    fig = plt.figure(figsize=(8, 4), num=f'bout generator i/o curve')
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0, 0])

    ax.plot(drives, m)
    ax.scatter(drives, m)
    ax.set_ylabel('mean motor output m')
    ax.set_xlabel('bout generator input u')
    ax.grid(True)

    if description is None:
        description = f'input-output curve for {cfg["boutgenerator.classname"]}'
    fig.suptitle(description)

    print('finished')
