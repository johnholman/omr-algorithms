import unittest

from simulator.sessrun.impacts import gv_impact, gv_impacts, cost_by_coord


class TestImpacts(unittest.TestCase):

    def setUp(self):
        self.dims = (3, 5)
        self.costs = (9, 4, 6, 4, 7,
                      6, 4, 12, 15, 3,
                      12, 7, 3, 6, 8)
        self.min_cost = 3
        self.best_coords = (1, 4)

    def test_cost_by_coord(self):
        self.assertEqual(cost_by_coord(self.best_coords, self.costs, self.dims), self.min_cost)
        self.assertEqual(cost_by_coord((2, 3), self.costs, self.dims), 6)

    def test_gv_impact(self):
        impact = gv_impact(0, self.best_coords, self.costs, self.dims, self.min_cost)
        self.assertEqual(impact, 5)
        impact = gv_impact(1, self.best_coords, self.costs, self.dims, self.min_cost)
        self.assertEqual(impact, 12)


    def test_central(self):
        costs = (9, 4, 6, 4, 7,
                 6, 4, 3, 15, 6,
                 12, 7, 3, 6, 8)
        impacts = gv_impacts(self.dims, costs)
        self.assertEquals(impacts, [3, 12])

    def test_corner(self):
        self.costs = (9, 4, 6, 4, 3,
                      6, 4, 3, 15, 6,
                      12, 7, 3, 6, 8)
        impacts = gv_impacts(self.dims, self.costs)
        self.assertEquals(impacts, [3, 1])


    def test_all_impacts(self):
        impacts = gv_impacts(self.dims, self.costs)
        self.assertEqual(impacts, [5, 12])



if __name__ == '__main__':
    unittest.main()
