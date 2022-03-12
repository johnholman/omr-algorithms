import math
import os

import pandas as pd
from matplotlib import pyplot as plt

from simulator.sessrun.fit import optimal_fit
from simulator.sessrun.util import get_data_folders


def create_figure(nplots=1, nrows=1, hsize=None, vsize=None, fig_name=None, size=None,
                  hspace=None, wspace=None, h_pad=None, w_pad=None):
    """Return figure and list of axes
    """

    mm = 0.0394  # convert millimeteres to inches

    ncolumns = math.ceil(nplots / nrows)

    # print(f'{nrows=} {ncolumns=}')

    if size is not None:
        hsize = size[0] * mm
        vsize = size[1] * mm

    # calculate defaults for figure size
    if vsize is None:
        if nrows == 1:
            vsize = 6
        elif nrows == 2:
            vsize = 8
        else:
            vsize = 10
    if hsize is None:
        if ncolumns == 1:
            hsize = 9
        elif ncolumns == 2:
            hsize = 12
        else:
            hsize = 15

    print(f'size in inches: {(hsize, vsize)}')
    _, project, expt_name = get_data_folders()

    fignum = f'{fig_name}' if fig_name else f'{expt_name} {next_fignum()}'
    fig = plt.figure(figsize=(hsize, vsize), num=fignum, constrained_layout=True)
    fig.set_constrained_layout_pads(w_pad=w_pad, h_pad=h_pad, wspace=wspace, hspace=hspace)

    axes = fig.subplots(nrows, ncolumns, squeeze=False)
    if nplots == 1:
        axes = axes[0][0]

    return fig, axes


def next_fignum():
    next_fignum.num += 1
    return next_fignum.num


next_fignum.num = 0


def save_figure(fig, fig_name, figdir, formats):
    if isinstance(formats, str):
        formats = [formats]
    for fmt in formats:
        fname = fig_name + '.' + fmt
        figpath = os.path.join(figdir, fname)
        figpath = os.path.normpath(os.path.expanduser(figpath))
        fig.savefig(figpath, bbox_inches='tight')
        # fig.savefig(figpath, bbox_inches='tight', pad_inches=0.5)


def get_errors(expts, measurements=None):
    errors = []
    for expt_name, project_name, features in expts.values():
        result = optimal_fit(expt_name=expt_name, project_name=project_name, features=features)
        rel_errs = result['rel_errs']
        rel_errs['cost'] = result['cost']
        rel_errs['features'] = features
        errors.append(rel_errs)
    df = pd.DataFrame(errors, index=expts.keys())

    if measurements is not None:
        col_names = [m + '_err_norm' if m != 'cost' else m for m in measurements.values()]
        new_names = measurements.keys()
        rename_map = {col_name: new_name for col_name, new_name in zip(tuple(col_names), tuple(new_names))}
        df = df[col_names].rename(columns=rename_map)
    return df
