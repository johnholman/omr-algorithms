import pandas as pd

from simulator.expt.actual import get_actual_summ
from simulator.reporting.figs import compare_fig
from simulator.sessrun.fit import compare_data
from simulator.sessrun.persist import retrieve_data
from simulator.sessrun.util import get_data


def compare_rpt(*, predicted, summ_fn, indep_vars, dep_vars, proc=None, actual_summ_path=None, actual_summ=None,
                **kwargs):
    if actual_summ is None:
        if actual_summ_path is not None:
            actual_summ = retrieve_data(actual_summ_path)
        elif proc is not None:
            actual_summ = get_actual_summ(proc)
        else:
            print("*** must provide actual data for comparison")
            return

    md, df = get_data(predicted)
    predicted_summ = summ_fn(df, period=-20)

    errs = compare_data(actual_summ, predicted_summ, md=md)

    print("\nFitting errors:")
    errs_df = pd.DataFrame([errs])
    print(errs_df.to_string(index=False, col_space=8, float_format=lambda x: "{:.3f}".format(x)))

    compare_fig(actual_summ, predicted_summ, md=md, indep_vars=indep_vars, dep_vars=dep_vars,
                **kwargs)


def set_pandas_options():
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.max_rows', 2000)
    pd.set_option('display.float_format', '{:.3f}'.format)
