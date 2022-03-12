import unittest
from unittest.mock import patch

import pandas as pd

from simulator.sessrun.fit import rel_errors, cost_errors


class TestCost(unittest.TestCase):

    def setUp(self):
        self.fit_df = pd.DataFrame([[3, 2, 5, 4], [1, 3, 3, 7]], columns=['a', 'x_err', 'y_err', 'z_err'])
        self.fit_df_copy = self.fit_df.copy()
        # print(self.fit_df)

        self.err_df = pd.DataFrame([[3, 2, 5, 4, 2.5, 0.5], [1, 3, 3, 7, 1.5, 0.75]],
                                   columns=['a', 'x_err', 'y_err', 'z_err', 'x_err_norm', 'y_err_norm'])

    def test_rel_errs(self):
        means = pd.Series({'x': 4, 'y': 2})
        with patch('simulator.sessrun.fit.get_means') as mock_get_means:
            mock_get_means.return_value = means
            errdf = rel_errors(self.fit_df)
            self.assertTrue(all(errdf.columns == self.err_df.columns))
            self.assertTrue(self.fit_df.equals(self.fit_df_copy), 'should not mutate original')
            self.assertTrue(all(errdf.x_err_norm == (0.5, 0.75)))

            if __name__ == '__main__':
                unittest.main()

    def test_cost_errors_single_factor(self):
        means = pd.Series({'x': 4, 'y': 2})
        with patch('simulator.sessrun.fit.get_means') as mock_get_means:
            mock_get_means.return_value = means

            features = [ 'x' ]
            cost_df = cost_errors(self.fit_df, features=features)
            self.assertTrue(all(cost_df.cost == ([0.5, 0.75])))

    def test_cost_errors_multiple_factor(self):
        means = pd.Series({'x': 4, 'y': 2})
        with patch('simulator.sessrun.fit.get_means') as mock_get_means:
            mock_get_means.return_value = means

            features = [ 'x', 'y' ]
            cost_df = cost_errors(self.fit_df, features=features)
            self.assertTrue(all(cost_df.cost == ([1.5, 1.125])))
