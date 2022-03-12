from unittest import TestCase

from simulator.sessrun.cache import ResultsCache


class TestCache(TestCase):

    def setUp(self):
        self.keynames = 'a_grid', 'b_grid'
        self.cache = ResultsCache(self.keynames, project_name='cache_test', expt_name='cache_test')
        self.cache.save()  # make sure we start we an empty cache file

    def test_save_retrieve(self):
        val1 = {'x_err': 3, 'y_err': 4}
        val2 = {'x_err': 12, 'y_err': 3}
        self.assertEqual(len(self.cache), 0)
        self.cache[(1, 2)] = val1
        self.assertEqual(self.cache[(1, 2)], val1)
        self.assertEqual(self.cache[{'z': 1, 'y': 2}], val1)
        self.cache[{'z': 1, 'y': 2.0001}] = val2
        self.assertEqual(self.cache[(1, 2.0001)], val2)
        self.assertEqual(len(self.cache), 2)
        self.cache.clear()
        self.assertEqual(len(self.cache), 0)

    def test_rounding(self):
        val1 = {'x_err': 3, 'y_err': 4}
        val2 = {'x_err': 12, 'y_err': 3}
        val3 = {'x_err': 15, 'y_err': 2}
        self.cache[(1, 2.0)] = val1
        self.cache[(1, 2.0001)] = val2
        self.assertEqual(self.cache[(1, 2)], val1)
        self.cache[(1, 2.0001000001)] = val3
        self.assertEqual(self.cache[(1, 2.0001)], val3)
        self.assertEqual(self.cache[(1, 2.00010000007)], val3)
        self.assertEqual(self.cache[(1, 2)], val1)

    def test_bad_keys(self):
        val1 = {'x_err': 3, 'y_err': 4}
        with self.assertRaises(ValueError, msg='bad key value'):
            self.cache[(1, 2, 3)] = val1
        with self.assertRaises(ValueError, msg='result must be dictionary'):
            self.cache[(3, 4)] = 27
        with self.assertRaises(ValueError, msg='result key cannot end with _grid'):
            self.cache[(3, 4)] = {'x_err': 3, 'y_grid': 4}


    def test_persist(self):
        self.assertFalse(self.cache.load())  # the cache is empty!
        key1 = (1.0, 2.3)
        val1 = {'x_err': 3, 'y_err': 4, 'y_np': 45}
        self.cache[key1] = val1
        key2 = (1.0, 2.300001)
        val2 = {'x_err': 5, 'y_err': 12.3, 'y_np': 6}
        self.cache[key2] = val2
        self.assertEqual(len(self.cache), 2)  # in fact two things
        self.cache.save()
        cache = ResultsCache(self.keynames, project_name='cache_test', expt_name='cache_test')
        self.assertTrue(cache.load())  # now it should contain something!
        self.assertEqual(len(cache), 2)  # in fact two things
        self.assertEqual(cache[key1], val1)
        self.assertEqual(cache[key2], val2)
        self.assertEqual(list(cache.olddf.columns), ['a_grid', 'b_grid', 'x_err', 'y_err', 'y_np'])


# if __name__ == "__main__":
#     main()
