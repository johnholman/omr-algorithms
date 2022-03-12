# runner for OMR simulations
import time
from pprint import pformat

from simulator.sessrun.md import MD
from simulator.sessrun.srunner import SessionRunner
from simulator.sessrun.util import get_expt_cfg, get_metadata, save_data, get_script_info


def run_expt(*, expt_name=None, project_name=None, save=False, description=None, cfg=None, vcfg=None, fmt=None,
             format=None, verbose=True,
             **_args):
    if cfg is None:
        cfg = {}
    if vcfg is None:
        vcfg = {}

    start = time.time()

    # support legacy fmt argument
    if format is None and fmt is not None:
        format = fmt

    default_name, default_project = get_script_info()
    if expt_name is None:
        expt_name = default_name

    if project_name is None:
        project_name = default_project

    if description is None:
        description = expt_name

    if verbose:
        print(f"Experiment name: {expt_name} project: {project_name}")

    expt_cfg = get_expt_cfg(cfg, vcfg)

    if verbose:
        print(f'Experiment config:\n{pformat(expt_cfg, depth=5)}\n')

    sr = SessionRunner(expt_cfg)
    sr.verbose = verbose
    df = sr.run_groups()

    md = get_metadata(expt_name, description, expt_cfg)

    if save:
        save_data(df, md, expt_name=expt_name, project_name=project_name, format=format)

    if verbose:
        print(f'Elapsed time {time.time() - start :.1f}')

    return MD(md), df
