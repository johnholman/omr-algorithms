from matplotlib import pyplot as plt

from figs.utils import create_figure

def trace_axes(fig_name, size=None):
    fig, ax = create_figure(size=size, fig_name=fig_name)
    ax.set_xlim(90, 100)
    ax.set_ylim(300, 500)
    ax.set_xlabel('time (s)')
    ax.set_ylabel('position (mm)')
    ax.scatter([0], [0], color='C0', s=1, label='candidate points')
    ax.plot([0], [0], color='black', linewidth=0.5, label='selected points')
    ax.legend(loc='upper left')
    return fig

def test():
    plt.rcParams['figure.max_open_warning'] = 50
    plt.rcParams['figure.titlesize'] = 9
    plt.rcParams['figure.constrained_layout.w_pad'] = 4 / 72
    plt.rcParams['figure.constrained_layout.h_pad'] = 4 / 72
    plt.rcParams['figure.constrained_layout.hspace'] = 0
    plt.rcParams['figure.constrained_layout.wspace'] = 0

    plt.rcParams['axes.labelsize'] = 7.5
    plt.rcParams['axes.titlesize'] = 7.5
    plt.rcParams['axes.labelpad'] = 3
    plt.rcParams['xtick.labelsize'] = 6.5
    plt.rcParams['ytick.labelsize'] = 6.5
    plt.rcParams['xtick.major.pad'] = 2
    plt.rcParams['ytick.major.pad'] = 1
    plt.rcParams['legend.fontsize'] = 7
    plt.rcParams['legend.title_fontsize'] = 7
    plt.rcParams['lines.linewidth'] = 1
    plt.rcParams['lines.markersize'] = 4

    trace_axes()
    plt.show()

if __name__ == '__main__':
    test()
