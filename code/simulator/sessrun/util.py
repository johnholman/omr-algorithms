import datetime
import os
import sys
from importlib import import_module
from itertools import product

import pandas as pd

from simulator.expt import defaultcfg as global_config
from simulator.sessrun.econfig import ExperimentConfig
from simulator.sessrun.md import MD
from simulator.sessrun.persist import retrieve_data, store_data


def get_data(dref=None):
    """Return data for the given data reference

    If dref is not specified the default names are used
    Otherwise dref is interpreted as the data itself
    """
    # print(get_info.cache_info())

    expt_name = None
    proj_name = None

    if isinstance(dref, str):
        load = True
        if ':' in dref:
            proj_name, expt_name = dref.split(':')
        else:
            expt_name = dref
    elif dref is None:
        load = True
        expt_name, _ = get_script_info()
    else:
        load = False

    if load:
        data = load_data(expt_name=expt_name, project_name=proj_name)
    else:
        data = dref

    return data


def load_data(filename=None, *, expt_name=None, project_name=None):
    # get path to the experiment folder
    base_path, project_folder, expt_folder = get_data_folders()
    if project_name is not None:
        project_folder = project_name
    if expt_name is not None:
        expt_folder = expt_name
    expt_path = os.path.join(base_path, project_folder, expt_folder)

    csvargs = {'dtype': {'group_id': str}}

    if filename is None:
        # loading primary data with metadata by default
        md, df = retrieve_data(expt_path, csvargs=csvargs)
        assert isinstance(df, pd.DataFrame)
        data = MD(md), df
    else:
        filepath = os.path.join(expt_path, filename)
        data = retrieve_data(filepath)
    return data


def save_data(df, metadata=None, *, filename=None, expt_name=None, project_name=None, format=None, float_format=None):
    # get path to the experiment folder
    base_path, project_folder, expt_folder = get_data_folders()
    if project_name is not None:
        project_folder = project_name
    if expt_name is not None:
        expt_folder = expt_name
    expt_path = os.path.join(base_path, project_folder, expt_folder)
    # print(f'save: {expt_path=}')

    if metadata is not None:
        # save primary data object along with metadata to the experiment folder
        store_data(expt_path, df, metadata=metadata, format=format)
    else:
        # save secondary data object within the experiment folder with given filename
        if filename is None:
            raise ValueError('fname required when saving without metadata')
        head, _ = os.path.split(filename)
        if head:
            raise ValueError('fname must not include directory')
        fpath = os.path.join(expt_path, filename)
        store_data(fpath, df, format=format, float_format=float_format)


def get_script_info():
    """Return module name and immediate containing package of calling script
    """
    # top-level script or module is imported with name __main__
    scriptpath = os.path.abspath(sys.modules["__main__"].__file__)
    rest, script_filename = os.path.split(scriptpath)
    rest, package_name = os.path.split(rest)
    module_name = os.path.splitext(script_filename)[0]
    # print(f'get_script_info: path {scriptpath} script: "{module_name}"  project: "{package_name}"')

    return module_name, package_name


def get_project_folder():
    """Return absolute path to the project folder"""
    base_path, project_folder, expt_folder = get_data_folders()
    return os.path.join(base_path, project_folder)


def get_experiment_folder():
    """Return absolute path to the experiment folder"""
    base_path, project_folder, expt_folder = get_data_folders()
    return os.path.join(base_path, project_folder, expt_folder)


def get_data_folders():
    """Return base path, project folder and experiment folder

    The project data folder is a subfolder of the base data folder found in configuration with the same
    name as the project.
    """
    base_data_folder = get_project_cfg('base_data_folder')
    # expand and normalise configured base data folder
    base_data_folder = os.path.abspath(os.path.normpath(os.path.expanduser(base_data_folder)))

    # check the folder already exists
    if not (os.path.isdir(base_data_folder)):
        raise Exception(f'Base data folder {base_data_folder} does not exist')

    expt_name, project_name = get_script_info()

    return base_data_folder, project_name, expt_name


def get_project_cfg(section):
    """Return a default configuration section for the current project.

    The requested sections from the global and project configuration files are retrieved and merged.
    Dictionary sections are merged with the project configuration taking priority. For string sections
    the project configuration section is returned if present, otherwise the global configuration section.
    """
    try:
        global_section = getattr(global_config, section)
    except AttributeError:
        raise Exception(f"Configuration section {section} not present in global default config file")

    # get project config
    _, project = get_script_info()
    try:
        project_cfg = import_module(".defaultcfg", project)

        # get required section from project config file
        proj_section = getattr(project_cfg, section, None)

        # use global section if not present in project config
        if proj_section is None:
            section_cfg = global_section
            # merge with global config if a dictionary
        elif isinstance(proj_section, dict):
            section_cfg = {**global_section, **proj_section}
        # replace global config if a string
        elif isinstance(proj_section, str):
            section_cfg = proj_section
        else:
            raise Exception(f"Invalid configuration section {section}")

    except ModuleNotFoundError:
        section_cfg = global_section
        # print(f'no configuration file for project "{project}"')

    return section_cfg


def get_expt_cfg(cfg, vcfg):
    """Return the experiment configuration generated from user-provided configuration

    This is returned as a dictionary suitable for saving as metadata as well as further processing
    """

    # ensure any provided group names are strings
    gnames = None
    if 'groups' in cfg:
        gnames = [str(gid) for gid in cfg['groups']]

    # expand the variable configuration to canonical form, generating default group names if not provided
    expanded_vcfg, gnames = expand_vcfg(vcfg, gnames)
    cfg['groups'] = gnames

    # merge user-provided fixed config with defaults for the project
    default_ecfg = get_project_cfg("experiment")
    cfg = {**default_ecfg, **cfg}

    # combine fixed and variable configurations to produce the experimental config
    expt_cfg = {'common': cfg, **expanded_vcfg, 'user_vcfg': vcfg}

    # add experiment and project names
    module_name, package_name = get_script_info()
    expt_cfg['name'] = module_name
    expt_cfg['project'] = package_name

    # if indep_vars not given explicitly default them from examination of the config
    if 'indep_vars' not in expt_cfg['common']:
        expt_cfg['common']['indep_vars'] = indep_variables(expt_cfg)

    return expt_cfg


def get_expt_dir():
    return get_project_cfg('expt_base_folder')


def expand_vcfg(vcfg, gnames=None):
    """Return the expanded variable configuration and groups names for the given
    user experiment configuration

    Default group names are generated if not provided
    """

    if isinstance(vcfg, list):
        evcfg, gnames = expand_list_vcfg(vcfg, gnames)
    elif isinstance(vcfg, dict) and vcfg != {}:
        v = next(iter(vcfg.values()))  # get value of first item in the vcfg dictionary
        if isinstance(v, list):  # if a list the variable config is in concise form and needs expansion
            evcfg, gnames = expand_compact_vcfg(vcfg, gnames)  # and expand variable part into canonical form
        else:
            evcfg, gnames = expand_full_vcfg(vcfg, gnames)
    else:
        raise ValueError(f'invalid variable configuration {vcfg}')

    return evcfg, gnames


def expand_full_vcfg(vcfg, gnames):
    evcfg = vcfg
    if gnames is None:
        raise ValueError('group list required')
    return evcfg, gnames


def expand_list_vcfg(vcfg, gnames):
    if gnames is None:
        gnames = [str(n) for n in range(1, len(vcfg) + 1)]
    if len(gnames) != len(vcfg):
        raise ValueError(f'group name list does not match variable config')
    evcfg = {'group ' + gname: cfg for cfg, gname in zip(vcfg, gnames)}
    return evcfg, gnames


def expand_compact_vcfg(vcfg, gnames=None):
    """Return the given compact variable configuration expanded to canonical form and the list of group names

    Default group names are generated if not provided
    """
    ivars = list(vcfg.keys())

    # generate all combinations of values, one combination for each group
    val_combos = list(product(*vcfg.values()))

    # generate default group names if not provided
    if gnames is None:
        gnames = [str(gnum) for gnum in range(1, len(val_combos) + 1)]

    # add a group specification for each combination of values
    # for example, if group 7 has values (1, -3) and independent variables are ('height', 'Vs') then
    # we add item 'group 7' : { 'height' : 1, 'Vs' : -3 } to the expanded vcfg dictionary

    evcfg = {}
    for gname, values in zip(gnames, val_combos):
        gcfg = {ivar: ival for ivar, ival in zip(ivars, values)}
        evcfg['group ' + gname] = gcfg

    # print(evcfg)
    return evcfg, gnames


def indep_variables(ecfg_dict):
    """ Return specification of independent variables in concise vcfg format.

    This only looks at config common to the group (i.e. phases disregarded)
    """
    ecfg = ExperimentConfig(ecfg_dict)

    groups = ecfg.get_config()['groups']

    d = {}
    for group in groups:
        cfg = ecfg.get_config(f'group {group}')
        for k, v in cfg.items():
            if k not in ('groups', 'phases', 'rgen'):
                if k in d.keys():  # if existing key and new value, add it to list
                    if v not in d[k]:
                        d[k].append(v)
                else:  # if not a new key add item with value in a list
                    d[k] = [v]
    # variable config consists of items with values varying between groups
    ivars = {k: v for k, v in d.items() if len(v) > 1}
    return ivars


def get_metadata(name, description, expt_cfg):
    """Return metadata dictionary for given name, description and experimental config."""
    date = datetime.datetime.today().strftime('%Y:%m:%d %H:%M:%S')
    folder = get_project_folder()
    rpt_cfg = get_project_cfg('report')

    md = {'name': name, 'folder': folder, 'description': description,
          'date': date, 'expt_cfg': expt_cfg, 'rpt_cfg': rpt_cfg
          }
    return md


def create_component(class_key, **cfg):
    """
    Return component with given configuration and random
    generator.

    The component classname is given as the value of key 'class_key' in cfg and
    the constructor signature is <component_class>(**cfg)
    """
    classname = cfg[class_key]
    module_name, classname = classname.rsplit(".", 1)
    module = import_module(module_name)
    cls = getattr(module, classname)
    return cls(**cfg)


def import_obj(obj_key, **cfg):
    """
    Import an object specified by name in config

    The name is the value of key 'obj_key' in cfg
    """
    obj_fullname = cfg[obj_key]
    module_name, obj_name = obj_fullname.rsplit(".", 1)
    module = import_module(module_name)
    obj = getattr(module, obj_name)
    return obj
