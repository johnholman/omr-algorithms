"""
Created on 15 Apr 2018

@author: john
"""
import unittest

from simulator.sessrun.econfig import ExperimentConfig


class Test(unittest.TestCase):

    def setUp(self):
        cfg = {
            'common': {'groups': [1, 2], 'phases': [1, 2, 3, 4], 'egg': 27, 'Kp': 3},
            'phase 2': {'gain': 1.0, 'water_speed': 0.2},
            'phase 4': {'gain': 1.0, 'water_speed': 0.2},
            'group 1, phase 1': {'gain': 0.5, 'water_speed': -0.1},
            'group 1, phase 3': {'gain': 0.5, 'water_speed': -0.1},
            'group 2, phase 1': {'gain': 2.0, 'water_speed': -0.4},
            'group 2, phase 3': {'gain': 2.0, 'water_speed': -0.4},
        }
        self.ecfg = ExperimentConfig(cfg)

    def test_phases(self):
        groups = self.ecfg.groups()
        self.assertEqual(groups, [1, 2])

    def test_defaults(self):
        dcfg = self.ecfg.defaults()
        self.assertTrue('egg' in dcfg)
        self.assertEqual(dcfg['egg'], 27)

    def test_get_config(self):
        cfg = self.ecfg.get_config('')
        self.assertEqual(cfg['egg'], 27)
        with self.assertRaises(KeyError):
            cfg['gain']
        self.assertEqual(type(cfg['rgen']).__name__, 'RandomState')

        cfg = self.ecfg.get_config('group 1, phase 1')
        self.assertEqual(cfg['gain'], 0.5)
        self.assertEqual(cfg['egg'], 27)
        cfg = self.ecfg.get_config('group 2')
        self.assertEqual(cfg['Kp'], 3)
        with self.assertRaises(KeyError):
            cfg['gain']
        cfg = self.ecfg.get_config('group 1, phase 2')
        self.assertEqual(cfg['gain'], 1.0)
        self.assertEqual(cfg['Kp'], 3)
        self.assertEqual(type(cfg['rgen']).__name__, 'RandomState')

    def test_levels_selector(self):
        self.assertEqual(self.ecfg.levels_selector(), '')
        self.assertEqual(self.ecfg.levels_selector(group=2), 'group 2')
        self.assertEqual(self.ecfg.levels_selector(phase=3), 'phase 3')
        self.assertEqual(self.ecfg.levels_selector(phase=3, group=4), 'group 4, phase 3')

    def test_specific_config(self):
        cfg = self.ecfg.specific_config(group=2)
        with self.assertRaises(KeyError):
            cfg['gain']
        self.assertEqual(cfg['Kp'], 3)

        cfg = self.ecfg.specific_config(group=2, phase=2)
        self.assertEqual(cfg['gain'], 1.0)
        self.assertEqual(cfg['Kp'], 3)


if __name__ == "__main__":
    unittest.main()
