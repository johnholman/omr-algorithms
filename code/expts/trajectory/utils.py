import os


def save_figs(figs, figdir, direction=None):
    for (height, ss), fig in figs:
        save_fig(fig, figdir, height, ss, direction)


def save_fig(fig, figdir, height, stimulus_speed, direction=None):
    """Save figure to given directory with filename formed from height and
    stimulus speed

    The figure is saved to different sub-directories according to type:
    forward or backward trajectory or whole session
    """
    if direction == 'F':
        subdir = 'forward'
    elif direction == 'B':
        subdir = 'backward'
    else:
        subdir = 'session'

    fname = '_'.join([height, str(stimulus_speed)]) + '.jpg'
    fpath = os.path.join(os.path.expanduser(figdir), subdir, fname)
    print(f'saving figure to {fpath}')
    fig.savefig(fpath)
