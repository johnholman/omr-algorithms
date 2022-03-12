import unittest

from simulator.sessrun.util import get_expt_cfg, indep_variables


class Test(unittest.TestCase):

    def setUp(self):
        self.vcfg1 = {'h': [2, 4, 6]}
        self.vcfg2 = {'h': [2, 4], 'g': [3, 5, 6]}
        self.vcfg3 = {'h': [2, 4], 'g': [3, 5, 6], 'k': [0, 1]}

        self.cfg = {
            'environment.classname': 'environment.expts.FreeSwimEnvironment',
            'controller.classname': 'agent.controller.pi.PIController',
            'boutgenerator.classname': 'agent.controller.boutgen.BGBallistic',

            'Ke': 15,
            'Ki': 0.15,
            'Kp': 2,
            'tau': 15,
        }

        self.full_cfg = {
            'groups': range(1, 10),
            'environment.classname': 'environment.expts.FreeSwimEnvironment',
            'controller.classname': 'agent.controller.pi.PIController',
            'boutgenerator.classname': 'agent.controller.boutgen.BGBallistic',

            'Ke': 15,
            'Ki': 0.15,
            'Kp': 2,
            'tau': 15,
            'height': 6
        }

        self.full_vcfg = {
            'group 1': {'height': 5, 'Vs': -2},
            'group 2': {'height': 5, 'Vs': -5},
            'group 3': {'height': 5, 'Vs': -10},
            'group 4': {'height': 10, 'Vs': -2},
            'group 5': {'height': 10, 'Vs': -5},
            'group 6': {'height': 10, 'Vs': -10},
            'group 7': {'height': 20, 'Vs': -2},
            'group 8': {'height': 20, 'Vs': -5},
            'group 9': {'height': 20, 'Vs': -10},
        }

        self.full_vcfg2 = {
            'group 1': {'height': 5, 'Vs': -2},
            'group 2': {'height': 5, 'Vs': -5},
            'group 3': {'height': 5, 'Vs': -10},
            'group 4': {'Vs': -2},
            'group 5': {'Vs': -5},
            'group 6': {'height': 10, 'Vs': -10},
            'group 7': {'height': 20, 'Vs': -2},
            'group 8': {'height': 20, 'Vs': -5},
            'group 9': {'height': 20, 'Vs': -10},
        }

        self.k4_cfg = {
            'groups': [1, 2, 3],
            'phases': ['initial', 'train', 'delay', 'test'],
            'controller.classname': 'agent.controller.pn.PosNegNLCompController',
            'boutgenerator.classname': 'agent.controller.boutgen.BGBallistic',

            'Kp': 1,
        }

        self.k4_vcfg = {
            'phase initial': {'duration': 20, 'gain': 5},
            'phase train': {'gain': 20},
            'phase delay': {'duration': 10, 'Vs': 5, 'gain': 0},
            'phase test': {'duration': 5, 'gain': 10, },
            'group 1, phase train': {'duration': 7},
            'group 2, phase train': {'duration': 15},
            'group 3, phase train': {'duration': 30},
        }

        # self.default_cfg = {'Ki': 9, 'Kp': 9, 'dt': 0.02}

    def test_get_expt_cfg2(self):
        expt_cfg = get_expt_cfg(self.cfg, self.vcfg2)
        self.assertEqual(expt_cfg['common']['groups'], [str(x) for x in range(1, 7)])
        self.assertEqual(expt_cfg['common']['indep_vars'], {'h': [2, 4], 'g': [3, 5, 6]})
        self.assertEqual(expt_cfg['group 1'], {'h': 2, 'g': 3})
        self.assertEqual(expt_cfg['group 6'], {'h': 4, 'g': 6})
        self.assertEqual(expt_cfg['common']['Ki'], 0.15)
        self.assertEqual(expt_cfg['common']['dt'], 0.01)
        self.assertEqual(expt_cfg['user_vcfg'], {'h': [2, 4], 'g': [3, 5, 6]})

    def test_get_expt_cfg3(self):
        expt_cfg = get_expt_cfg(self.cfg, self.vcfg3)
        self.assertEqual(expt_cfg['common']['groups'], [str(x) for x in range(1, 13)])
        self.assertEqual(expt_cfg['common']['indep_vars'], {'h': [2, 4], 'g': [3, 5, 6], 'k': [0, 1]})
        self.assertEqual(expt_cfg['group 1'], {'h': 2, 'g': 3, 'k': 0})
        self.assertEqual(expt_cfg['group 12'], {'h': 4, 'g': 6, 'k': 1})
        self.assertEqual(expt_cfg['common']['Ki'], 0.15)
        self.assertEqual(expt_cfg['common']['dt'], 0.01)
        self.assertEqual(expt_cfg['user_vcfg'], {'h': [2, 4], 'g': [3, 5, 6], 'k': [0, 1]})

    def test_get_expt_k4(self):
        expt_cfg = get_expt_cfg(self.k4_cfg, self.k4_vcfg)
        self.assertEqual(expt_cfg['common']['indep_vars'], {})
        self.assertEqual(expt_cfg['common']['groups'], [str(x) for x in range(1, 4)])
        self.assertEqual(expt_cfg['group 1, phase train'], {'duration': 7})
        self.assertEqual(expt_cfg['common']['Kp'], 1)
        self.assertEqual(expt_cfg['common']['dt'], 0.01)

    def test_get_ivars2(self):
        ecfg = get_expt_cfg(self.cfg, self.vcfg2)
        d = indep_variables(ecfg)
        self.assertEqual(d, {'h': [2, 4], 'g': [3, 5, 6]})

    def test_get_ivars3(self):
        ecfg = get_expt_cfg(self.cfg, self.vcfg3)
        #         print(f'third config \n {ecfg}')
        d = indep_variables(ecfg)
        self.assertEqual(d, self.vcfg3)

    def test_get_ivars_full(self):
        ecfg = get_expt_cfg(self.full_cfg, self.full_vcfg)
        #         print(f'full ecfg\n {ecfg}')
        d = indep_variables(ecfg)
        vcfg = {'height': [5, 10, 20], 'Vs': [-2, -5, -10]}
        self.assertEqual(d, vcfg)

    def test_get_ivars_full_with_default(self):
        ecfg = get_expt_cfg(self.full_cfg, self.full_vcfg2)
        #         print(f'full ecfg\n {ecfg}')
        d = indep_variables(ecfg)
        vcfg = {'height': [5, 6, 10, 20], 'Vs': [-2, -5, -10]}
        self.assertEqual(d, vcfg)


if __name__ == "__main__":
    unittest.main()
