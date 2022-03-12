from pprint import pformat

import pandas as pd
from simulator.sessrun.econfig import ExperimentConfig
from simulator.sessrun.util import create_component


def msg(s, verbose=True):
    if verbose:
        print(s)


class SessionRunner(object):
    def __init__(self, ecfg):
        self.ecfg = ExperimentConfig(ecfg)
        self.session = None
        self.verbose = True

    def run_groups(self):
        dfs = []
        group_ids = self.ecfg.groups()
        for group_id in group_ids:
            dfs.append(self.run_group(group_id))
        df = pd.concat(dfs, keys=group_ids, names=['group_id'])
        return df.reset_index()  # reset index to turn index columns into data columns

    def run_group(self, group_id):
        group_cfg = self.ecfg.specific_config(group=group_id)

        assert 'nsubjects' in group_cfg.keys(), 'nsubjects config missing'
        subj_ids = range(1, group_cfg['nsubjects'] + 1)

        dfs = []
        for subj_id in subj_ids:
            dfs.append(self.run_subject(subj_id, group_id))
        return pd.concat(dfs, keys=subj_ids, names=['subj_id'])

    def run_subject(self, subj_id, group_id):
        group_cfg = self.ecfg.specific_config(group=group_id)
        if subj_id == 1:
            self.msg(f"config for group {group_id}\n{pformat(group_cfg, depth=2)}\n")

        assert 'session.classname' in group_cfg.keys(), 'must specify session.classname in config'
        self.session = create_component('session.classname', **group_cfg)
        phase_ids = self.ecfg.phases()
        data = []
        for phase_id in phase_ids:
            phase_data = self.run_phase(group_id, subj_id, phase_id)
            data.append(phase_data)

        df = pd.concat(data, keys=phase_ids, names=['phase_id'])

        return df

    def run_phase(self, group_id, subj_id, phase_id):
        data = []
        phase_cfg = self.ecfg.specific_config(group=group_id, phase=phase_id)

        self.session.configure(phase_cfg)
        #         print(f'group {group_id} phase {phase_id} config:\n{pformat(phase_cfg, depth=2)}')
        if subj_id == 1:
            self.msg(f"session configured for group {group_id} phase {phase_id}\n{self.session}\n")

        assert 'ntrials' in phase_cfg.keys(), 'ntrials config missing'
        trials = range(1, phase_cfg['ntrials'] + 1)
        for trial_id in trials:
            trial_data = self.run_trial(trial_id, phase_cfg)
            data += trial_data
        # workaround to maintain order of columns - should be fixed in Pandas
        columns = list(data[0].keys()) if len(data) > 0 else None
        df = pd.DataFrame(data, columns=columns)
        df = df.set_index(['trial_id', 'step_num'])
        return df

    def run_trial(self, trial_id, phase_cfg):
        nsteps = int(phase_cfg['duration'] / phase_cfg['dt'])
        timesteps = range(1, nsteps + 1)
        data = []

        for step in timesteps:
            self.session.update()
            rec = {'trial_id': trial_id, 'step_num': step}
            self.session.record(rec)
            data.append(rec)
            if self.session.finished():
                break
        return data

    def msg(self, s):
        if self.verbose:
            print(s)
