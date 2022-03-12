from itertools import chain, combinations
import numpy as np


class ExperimentConfig(object):
    def __init__(self, ecfg):
        self.ecfg = ecfg
        self.common_cfg = ecfg['common']
        if 'seed' in self.common_cfg:
            seed = self.common_cfg['seed']
        else:
            seed = None
        self.rgen = np.random.RandomState(seed)

    def defaults(self):
        return self.get_config()

    def phases(self):
        return self.common_cfg['phases']

    def groups(self):
        return self.common_cfg['groups']

    def specific_config(self, **spec):
        #         selector = (('group', group), ('phase', phase))
        select_str = self.levels_selector(**spec)
        #         print(f'specific config spec {spec} select string "{select_str}"')
        return self.get_config(select_str)

    @staticmethod
    def levels_selector(**spec):
        ls = []
        if 'group' in spec:
            ls.append(f'group {spec["group"]}')
        if 'phase' in spec:
            ls.append(f'phase {spec["phase"]}')
        return ', '.join(ls)

    def get_config(self, select_str=''):
        """Return experimental config for the given selection string.

        Example selection strings:
        '' : config items common to all groups and phases
        'group 1' : config items common to all phases for group 1
        'group 1, phase 3': config items for this group and phase
        """

        select_strings = ['common']

        if select_str != '':
            # transform select string into a list of associated config keys
            # for example, 'group 1, phase 3' becomes [ 'common', 'group 1', 'phase 3', 'group 1, phase 3' ]  
            selector = [clause.split() for clause in select_str.split(',')]
            #             print(f'selector {selector}')
            tlist = self.powerset(selector)[1:]
            #             print(f'select tuples {tlist}')
            for selector in tlist:
                ss = [f'{name} {value}' for name, value in selector]
                select_strings.append(', '.join(ss))

                # retrieve and merge dictionaries for each key in list to form the overall configuration
        #         print(f'select_strings {select_strings}')
        config = {}
        for selector in select_strings:
            if selector in self.ecfg.keys():
                newcfg = self.ecfg[selector]
                config = {**config, **newcfg}

        # add the random generator
        config['rgen'] = self.rgen
        return config

    @staticmethod
    def powerset(iterable):
        """ from itertools documentation but returns a list
        powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
        """
        s = list(iterable)  # allows duplicate elements
        p = chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))
        return list(p)


def config_item(cfg, attr, **selector):
    return ExperimentConfig(cfg).specific_config(**selector)[attr]


if __name__ == "__main__":
    def test():
        from pprint import pformat

        dt = 0.01
        seed = 2
        # levels = {
        #     'groups': (1, 2), 'phases': (1, 2, 3, 4),
        # }

        top_cfg = {
            'dt': dt,
            'seed': seed,
            'session.classname': 'simulator.session.Session',
            'agent.classname': 'simulator.agent.agent.Agent',
            'environment.classname': 'simulator.environment.simpleenv.SimpleEnvironment',
            'body.classname': 'simulator.agent.body.Body',
            'controller.classname': 'simulator.agent.controller.pibout.PIBoutController',
            'boutgenerator.classname': 'simulator.agent.controller.boutgen.BGFixedAtStart',
            'Ki': 1.0,  # integral gain for primary velocity controller
            'Kp': 0,
            'tau': 15,  # time constant for decay of effectiveness variable (= DRN activity)
            'Kb': 4,  # gain constant for effect of visual flow on effectiveness
            'initial_effectiveness': 2,
            # initial effectiveness - reflects prior belief in medium gain and medium water speed
            'Kstart': 2,  # rate coefficient for starting a bout
            'Kduration': 0.1,
            'Kintensity': 1,
            'Kstd': 0.1,
            #     'water_speed' : water_speed,
            #     'gain' : low_gain,
            'ntrials': 1,
            #         'nsteps' : 1000,
            'nsubjects': 20,
            'duration': 40,
            'groups': [1, 2],
            'phases': [1, 2, 3, 4],
        }

        cfg = {
            'common': top_cfg,
            'phase 2': {'gain': 1.0, 'water_speed': 0.2},
            'phase 4': {'gain': 1.0, 'water_speed': 0.2},
            'group 1, phase 1': {'gain': 0.5, 'water_speed': -0.1},
            'group 1, phase 3': {'gain': 0.5, 'water_speed': -0.1},
            'group 2, phase 1': {'gain': 2.0, 'water_speed': -0.4},
            'group 2, phase 3': {'gain': 2.0, 'water_speed': -0.4},
        }

        ecfg = ExperimentConfig(cfg)

        print(f'cfg: \n{pformat(cfg, depth=2)}\n')

        print(f'phases {ecfg.phases()} groups {ecfg.groups()}\n')

        cfg = ecfg.defaults()
        print(f'select default :\n{pformat(cfg, depth=2)}\n')

        select = 'group 1, phase 1'
        cfg = ecfg.get_config(select)
        print(f'select: {select}\nconfig:\n{pformat(cfg, depth=2, compact=True)}\n')

        select = 'group 2'
        cfg = ecfg.get_config(select)
        print(f'select: {select}\nconfig:\n{pformat(cfg, depth=2)}\n')

        cfg = ecfg.specific_config(group=2)
        print(f'as above with specific config\nconfig:\n{pformat(cfg, depth=2)}\n')

        select = 'group 2, phase train'
        cfg = ecfg.get_config(select)
        print(f'select: {select}\nconfig:\n{pformat(cfg, depth=2)}\n')

        cfg = ecfg.specific_config(group=2, phase='train')
        print(f'select g2 p train\nconfig:\n{pformat(cfg, depth=2)}\n')


    test()
