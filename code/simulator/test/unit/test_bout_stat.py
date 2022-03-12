import unittest
import pandas as pd
import numpy as np

from simulator.analysis.summary import nonterminating_bout_stats


class Test(unittest.TestCase):
    premature_threshold = 10.0
    subliminal_threshold = 6.0

    def stats(self, data, valid_starts, last):
        init_steps = 3
        numvalid = len(valid_starts)
        if numvalid == 0:
            return 0.0, np.nan, np.nan
        first = valid_starts[0]
        bout_rate = numvalid / (data.iloc[last]['time'] - data.iloc[first]['time'])
        bout_dist = (data.iloc[last]['position'] - data.iloc[first]['position']) / numvalid
        speeds = [data.iloc[start:start + init_steps].swim_speed.mean() for start in valid_starts]
        print(f'{speeds=}')
        bout_init_speed = sum(speeds) / len(speeds)
        return bout_rate, bout_dist, bout_init_speed

    def test_no_bouts(self):
        data = [
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, 'position': 2, 'time': 10.1},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 10, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 20, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 3, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 7, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 6, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, 'position': 4, 'time': 10.18},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
        ]
        df = pd.DataFrame(data)
        s = nonterminating_bout_stats(df, initial_duration=0.03, premature_threshold=Test.premature_threshold,
                                      subliminal_threshold=Test.subliminal_threshold)
        valid_starts = []
        num_premature = 0
        num_subliminal = 0
        bout_rate = 0.0
        bout_init_speed = bout_dist = np.nan
        self.assertEqual(s.num_bouts, len(valid_starts))
        self.assertEqual(s.num_premature, num_premature)
        self.assertEqual(s.num_subliminal, num_subliminal)
        self.assertTrue(np.isclose(s.bout_rate, bout_rate, equal_nan=True))
        self.assertTrue(np.isclose(s.bout_dist, bout_dist, equal_nan=True))
        self.assertTrue(np.isclose(s.bout_init_speed, bout_init_speed, equal_nan=True))

    def test_one_bout_at_start(self):
        data = [
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, 'position': 2, 'time': 10.1},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 10, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 20, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 3, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 7, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 6, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, 'position': 4, 'time': 10.18},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
        ]
        df = pd.DataFrame(data)
        s = nonterminating_bout_stats(df, initial_duration=0.03, premature_threshold=Test.premature_threshold,
                                      subliminal_threshold=Test.subliminal_threshold)
        valid_starts = []
        num_premature = 0
        num_subliminal = 0
        bout_rate = 0.0
        bout_init_speed = bout_dist = np.nan
        self.assertEqual(s.num_bouts, len(valid_starts))
        self.assertEqual(s.num_premature, num_premature)
        self.assertEqual(s.num_subliminal, num_subliminal)
        self.assertTrue(np.isclose(s.bout_rate, bout_rate, equal_nan=True))
        self.assertTrue(np.isclose(s.bout_init_speed, bout_init_speed, equal_nan=True))
        self.assertTrue(np.isclose(s.bout_dist, bout_dist, equal_nan=True))

    def test_calc1(self):
        data = [
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 5, 'position': 2, 'time': 10.1},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 10, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 20, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 2, },
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 7, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 6, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, 'position': 4, 'time': 10.18},
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
        ]
        df = pd.DataFrame(data)
        s = nonterminating_bout_stats(df, initial_duration=0.03, premature_threshold=Test.premature_threshold,
                                      subliminal_threshold=Test.subliminal_threshold)
        valid_starts = [2]
        last = 9
        bout_rate, bout_dist, bout_init_speed = self.stats(df, valid_starts, last)
        print(s)
        self.assertEqual(s.num_bouts, 1)
        self.assertEqual(s.num_premature, 0)
        self.assertEqual(s.num_subliminal, 1)
        self.assertAlmostEqual(s.bout_rate, bout_rate)
        self.assertAlmostEqual(s.bout_dist, bout_dist)
        self.assertAlmostEqual(s.bout_init_speed, bout_init_speed)

    def test_one_bout(self):
        data = [
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, 'position': 2, 'time': 10.1},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 10, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 20, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 3, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 7, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 6, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, 'position': 4, 'time': 10.18},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 8, },
        ]
        df = pd.DataFrame(data)
        s = nonterminating_bout_stats(df, initial_duration=0.03, premature_threshold=Test.premature_threshold,
                                      subliminal_threshold=Test.subliminal_threshold)
        valid_starts = []
        last = 11
        num_premature = 0
        num_subliminal = 0
        bout_rate, bout_dist, bout_init_speed = self.stats(df, valid_starts, last)
        print(s)
        self.assertEqual(s.num_bouts, len(valid_starts))
        self.assertEqual(s.num_premature, num_premature)
        self.assertEqual(s.num_subliminal, num_subliminal)
        self.assertTrue(np.isclose(s.bout_rate, bout_rate, equal_nan=True))
        self.assertTrue(np.isclose(s.bout_init_speed, bout_init_speed, equal_nan=True))
        self.assertTrue(np.isclose(s.bout_dist, bout_dist, equal_nan=True))

    def test_none_valid(self):
        data = [
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 5, 'position': 2, 'time': 10.1},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 6, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 3, },
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 7, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 6, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, 'position': 4, 'time': 10.18},
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
        ]
        df = pd.DataFrame(data)
        s = nonterminating_bout_stats(df, initial_duration=0.03, premature_threshold=Test.premature_threshold,
                                      subliminal_threshold=Test.subliminal_threshold)
        valid_starts = []
        last = 9
        num_premature = 0
        num_subliminal = 2
        bout_rate, bout_dist, bout_init_speed = self.stats(df, valid_starts, last)
        print(s)
        self.assertEqual(s.num_bouts, len(valid_starts))
        self.assertEqual(s.num_premature, num_premature)
        self.assertEqual(s.num_subliminal, num_subliminal)
        self.assertTrue(np.isclose(s.bout_rate, bout_rate, equal_nan=True))
        self.assertTrue(np.isclose(s.bout_dist, bout_dist, equal_nan=True))
        self.assertTrue(np.isclose(s.bout_init_speed, bout_init_speed, equal_nan=True))

    def test_calc2(self):
        data = [
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, },
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 5, 'position': 2, 'time': 10.1},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 10, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 20, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 2, },
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 7, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 6, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 20, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, 'position': 4, 'time': 10.18},
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
        ]
        df = pd.DataFrame(data)
        s = nonterminating_bout_stats(df, initial_duration=0.03, premature_threshold=Test.premature_threshold,
                                      subliminal_threshold=Test.subliminal_threshold)
        valid_starts = [2, 6]
        last = 9
        num_premature = 0
        num_subliminal = 0
        bout_rate, bout_dist, bout_init_speed = self.stats(df, valid_starts, last)
        print(s)
        self.assertEqual(s.num_bouts, len(valid_starts))
        self.assertEqual(s.num_premature, num_premature)
        self.assertEqual(s.num_subliminal, num_subliminal)
        self.assertAlmostEqual(s.bout_rate, bout_rate)
        self.assertAlmostEqual(s.bout_dist, bout_dist)
        self.assertAlmostEqual(s.bout_init_speed, bout_init_speed)

    def test_initial_start(self):
        data = [
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 10, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 20, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 2, },
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 7, 'position': 2, 'time': 10.04},
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 6, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 20, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 4, 'position': 4, 'time': 10.07},
            {'dt': 0.01, 'start_bout': True, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
            {'dt': 0.01, 'start_bout': False, 'swim_speed': 5, },
        ]
        df = pd.DataFrame(data)
        s = nonterminating_bout_stats(df, initial_duration=0.03, premature_threshold=Test.premature_threshold,
                                      subliminal_threshold=Test.subliminal_threshold)
        valid_starts = [4]
        last = 7
        num_premature = 0
        num_subliminal = 0
        bout_rate, bout_dist, bout_init_speed = self.stats(df, valid_starts, last)
        print(s)
        self.assertEqual(s.num_bouts, len(valid_starts))
        self.assertEqual(s.num_premature, num_premature)
        self.assertEqual(s.num_subliminal, num_subliminal)
        self.assertAlmostEqual(s.bout_rate, bout_rate)
        self.assertAlmostEqual(s.bout_dist, bout_dist)
        self.assertAlmostEqual(s.bout_init_speed, bout_init_speed)


if __name__ == "__main__":
    unittest.main()
