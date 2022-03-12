import unittest
from unittest.mock import patch

import pandas as pd

from simulator.sessrun.fit import grad_points_fd, grad_fd, cost_with_gradient


class TestGradient(unittest.TestCase):

    def setUp(self):
        pass

    def test_grad_points_fd(self):
        point = (1, 2)
        grad_steps = (0.5, 100)
        gpoints = grad_points_fd(point, grad_steps)
        self.assertEqual(gpoints, [(1.5, 2), (1, 102)])

    def test_grad_fd(self):
        y = 20  # cost at point to be evaluated
        grad_y = (18, 30)  # costs after steps in both directions
        steps = (0.5, 100)  # step sizes
        grad = grad_fd(y, grad_y, steps)
        self.assertEqual(grad, (-4, 0.1))

    def test_cost_with_gradient(self):
        cost_result = pd.DataFrame({'cost': [20, 18, 30], 'foo': [9, 8, 7]})
        with patch('simulator.sessrun.fit.cost_points')as mock_cost:
            mock_cost.return_value = cost_result
            point = (1, 2)
            grad_steps = (0.5, 100)
            cost, cost_grad, results = cost_with_gradient(point=point, grad_steps=grad_steps)
            self.assertEqual(cost, 20)
            self.assertEqual(cost_grad, (-4, 0.1))
            self.assertTrue(results.equals(cost_result))


if __name__ == '__main__':
    unittest.main()


def cost_points(points):
    return (20, 18, 30)
