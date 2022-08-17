""" Compile table of errors from a list of fitting experiments"""
import numpy as np
from matplotlib import pyplot as plt

from figs.utils import get_errors, create_figure


def errs_fig(expts, measurements, *, fig_name=None, primary='expt', x_label=None, y_label='relative prediction error',
             **kwargs):
    print(f'generating {fig_name}')

    err_df = get_errors(expts, measurements)

    print(err_df)

    if primary != 'expt':
        err_df = err_df.transpose()

    fig, ax = create_figure(fig_name=fig_name, **kwargs)

    grouped_bar_chart(ax, err_df, x_label=x_label, y_label=y_label, **kwargs)

    return fig


def grouped_bar_chart(ax, data_df, *, legend_title=None, x_label=None, y_label=None, grid=False, **_kwargs):
    nrows = len(data_df)
    ncols = len(data_df.columns)

    wid = 1 / (ncols + 1)  # leave one bar space between each group
    x0 = np.arange(nrows)  # position of first bar in each group

    colors = ('pink', 'turquoise', 'gold')
    for m, (var, color) in enumerate(zip(data_df.columns, colors)):
        x = x0 + m * wid
        y = data_df[var]
        ax.bar(x, y, wid, color=color)

    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)

    ncols = len(data_df.columns)
    xtick = x0 + ((ncols - 1) / 2) * wid  # place label in centre of group of bars
    ax.set_xticks(xtick)
    ax.set_xticklabels(data_df.index)
    ax.legend(title=legend_title, labels=data_df.columns, frameon=False,)
    ax.grid(grid)

# def grouped_bar_chart(ax, data_df, *, legend_title=None, x_label=None, y_label=None, grid=False, **_kwargs):
#     nrows = len(data_df)
#     ncols = len(data_df.columns)
#
#     wid = 1 / (ncols + 1)  # leave one bar space between each group
#     x0 = np.arange(nrows)  # position of first bar in each group
#
#     for m, col in enumerate(data_df.columns):
#         x = x0 + m * wid
#         y = data_df[col]
#         ax.bar(x, y, wid)
#
#     ax.set_ylabel(y_label)
#     ax.set_xlabel(x_label)
#
#     ncols = len(data_df.columns)
#     xtick = x0 + ((ncols - 1) / 2) * wid  # place label in centre of group of bars
#     ax.set_xticks(xtick)
#     ax.set_xticklabels(data_df.index)
#     ax.legend(title=legend_title, labels=data_df.columns, frameon=False,)
#     ax.grid(grid)
#
def test():
    ri = ['bout_rate', 'bout_init_speed']

    expts = {
        'basic': ('li_single_ribo_fit', 'pub21', ri),
        'A': ('pmi_li_ribo_fit_plus', 'pub21', ri),
        'B': ('pmi_fbli_ribo_fit_plus', 'pub21', ri),
        'C': ('pmi_fli_ribo_fit_plus', 'pub21', ri),
    }

    measurements = {
        'bout rate': 'bout_rate',
        'bout intensity': 'bout_init_speed',
        # 'overall bout fit': 'cost',
        'swim speed': 'swim_speed',
    }

    fig_name = '3.13 test - prediction errors for model 3 variants'
    errs_fig(expts, measurements=measurements, fig_name=fig_name)


if __name__ == '__main__':
    test()

    plt.show()
