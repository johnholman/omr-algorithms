import unittest

from simulator.sessrun.util import expand_vcfg, expand_compact_vcfg


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

        self.default_cfg = {'Ki': 9, 'Kp': 9, 'dt': 0.02}

        self.lvcfg = [
            {'height': 8, 'stimulus_speed': 0.8},
            {'height': 8, 'stimulus_speed': 1.6},
            {'height': 8, 'stimulus_speed': 2.4},
            {'height': 32, 'stimulus_speed': 3.2},
            {'height': 32, 'stimulus_speed': 6.4},
            {'height': 32, 'stimulus_speed': 9.6},
        ]

    def test_expand_compact1(self):
        vcfg = {'h': [2, 4], 'g': [3, 5, 6]}

        evcfg, gnames1 = expand_compact_vcfg(vcfg, gnames=None)
        gnames = ['1', '2', '3', '4', '5', '6']

        self.assertEqual(gnames1, gnames)
        self.assertEqual(evcfg['group 1'], {'h': 2, 'g': 3})
        self.assertEqual(evcfg['group 5'], {'h': 4, 'g': 5})

        gnames = ['a', 'b', 'c', 'd', 'e', 'f']
        evcfg, gnames1 = expand_compact_vcfg(vcfg, gnames)
        self.assertEqual(gnames1, gnames)
        self.assertEqual(evcfg['group a'], {'h': 2, 'g': 3})
        self.assertEqual(evcfg['group e'], {'h': 4, 'g': 5})

    def test_expand_compact2(self):
        vcfg = {'h': [2, 4], 'g': [3, 5, 6], 'k': [0, 1]}
        evcfg, gnames1 = expand_compact_vcfg(vcfg, gnames=None)
        self.assertEqual(list(evcfg['group 1'].keys()), ['h', 'g', 'k'])
        self.assertEqual(list(evcfg['group 1'].values()), [2, 3, 0])
        self.assertEqual(list(evcfg['group 12'].values()), [4, 6, 1])

    def test_expand_vcfg1(self):
        gnames = ['a', 'b', 'c']
        evcfg, groups = expand_vcfg(self.full_vcfg, gnames)
        self.assertEqual(groups, gnames)
        self.assertEqual(evcfg, self.full_vcfg)

    def test_expand_vcfg2(self):
        gnames = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        evcfg, gnames1 = expand_vcfg(self.vcfg2, gnames)
        self.assertEqual(gnames1, gnames)
        self.assertEqual(list(evcfg['group a'].keys()), ['h', 'g'])
        self.assertEqual(evcfg['group a'], {'h': 2, 'g': 3})
        self.assertEqual(evcfg['group f'], {'h': 4, 'g': 6})

    def test_expand_vcfg3(self):
        vcfg = {'h': [2, 4], 'g': [3, 5, 6]}
        evcfg = {
            'group 1': {'h': 2, 'g': 3},
            'group 2': {'h': 2, 'g': 5},
            'group 3': {'h': 2, 'g': 6},
            'group 4': {'h': 4, 'g': 3},
            'group 5': {'h': 4, 'g': 5},
            'group 6': {'h': 4, 'g': 6},
        }
        gnames = ['1', '2', '3', '4', '5', '6']

        evcfg1, gnames1 = expand_vcfg(vcfg)
        self.assertEqual(gnames1, gnames)
        self.assertEqual(evcfg1, evcfg)

    def test_expand_vcfg4(self):
        vcfg = [
            {'height': 8, 'stimulus_speed': 0.8},
            {'height': 8, 'stimulus_speed': 1.6},
            {'height': 8, 'stimulus_speed': 2.4},
            {'height': 32, 'stimulus_speed': 3.2},
            {'height': 32, 'stimulus_speed': 6.4},
            {'height': 32, 'stimulus_speed': 9.6},
        ]

        ecfg = {
            'group 1': {'height': 8, 'stimulus_speed': 0.8},
            'group 2': {'height': 8, 'stimulus_speed': 1.6},
            'group 3': {'height': 8, 'stimulus_speed': 2.4},
            'group 4': {'height': 32, 'stimulus_speed': 3.2},
            'group 5': {'height': 32, 'stimulus_speed': 6.4},
            'group 6': {'height': 32, 'stimulus_speed': 9.6},
        }

        groups = ['1', '2', '3', '4', '5', '6']

        ecfg1, groups1 = expand_vcfg(vcfg)
        self.assertEqual(ecfg1, ecfg)
        self.assertEqual(groups1, groups)

        groups = ['a', 'b', 'c', 'd', 'e', 'f']
        ecfg = {
            'group a': {'height': 8, 'stimulus_speed': 0.8},
            'group b': {'height': 8, 'stimulus_speed': 1.6},
            'group c': {'height': 8, 'stimulus_speed': 2.4},
            'group d': {'height': 32, 'stimulus_speed': 3.2},
            'group e': {'height': 32, 'stimulus_speed': 6.4},
            'group f': {'height': 32, 'stimulus_speed': 9.6},
        }
        ecfg1, groups1 = expand_vcfg(vcfg, groups)
        self.assertEqual(ecfg1, ecfg)
        self.assertEqual(groups1, groups)

        groups = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        with self.assertRaises(ValueError, msg='wrong number of groups given'):
            expand_vcfg(vcfg, groups)

    # def test_get_expt_cfg(self):
    #     expt_cfg = get_expt_cfg(self.full_cfg, self.full_vcfg)
    #     pprint(expt_cfg)


if __name__ == "__main__":
    unittest.main()
