from matplotlib import pyplot as plt

from simulator.analysis.report import indiv_rpt_expt, group_rpt_expt, summary_rpt_expt
from simulator.sessrun.erunner import run_expt


def run(*, name=None, indiv_report=True, save=True, **args):
    """Run experiment and generate a generic report

    If name is not given, the base filename without extension of the calling module
    is used to provide the name
    """
    data = run_expt(name=name, save=save, **args)
    if indiv_report:
        indiv_rpt_expt(data, **args)
    group_rpt_expt(data, **args)
    summary_rpt_expt(data, **args)
    plt.show()
