import os

from simulator.sessrun.persist import retrieve_data
from simulator.sessrun.util import get_project_cfg


def get_actual_dir(proc=None):
    """
    Return directory path for actual data for the given procedure or all procedures
    :param proc: procedure code, or base directory if None (default)
    :return: path to the data
    """
    cfg = get_project_cfg('actual')
    path = cfg['base_folder']
    path = os.path.abspath(os.path.normpath(os.path.expanduser(path)))
    if proc is not None:
        type_map = cfg['type_map']
        if proc not in type_map:
            raise ValueError(f'{proc}: no such procedure')
        subdir = cfg['type_map'][proc]
        path = os.path.join(path, subdir)
    return path


def get_actual_summ(proc=None, full=False):
    """
    Return experimental data for the given procedure or all procedures
    :param proc: procedure code, or data for all procedures if None (default)
    :param full: whether to return all data or data excluding outliers
    :return: the data
    """
    if proc is None:
        proc = 'ALL'
    fname = 'group_summ' if full else 'group_summ_pruned'
    folder = get_actual_dir(proc)
    df = retrieve_data(os.path.join(folder, fname))
    return df


def test():
    print(get_actual_dir())
    print(get_actual_dir('BF'))
    print(get_actual_dir('ALL'))
    try:
        print(get_actual_dir('zzz'))
    except ValueError as e:
        print(f"exception {e}")

    df = get_actual_summ()
    print(df.head())

    df = get_actual_summ(full=True)
    print(df.head())

    df = get_actual_summ(proc='BF')
    print(df.head())

    df = get_actual_summ(proc='OR', full=True)
    print(df.head())


if __name__ == "__main__":
    test()
