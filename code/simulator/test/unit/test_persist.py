from unittest import TestCase

from simulator.sessrun.persist import set_base, retrieve_data, store_data
import os

import numpy as np
import pandas as pd


class TestPersist(TestCase):

    def setUp(self):
        base = r'~\temp\data\persist_tests'
        base = os.path.normpath(os.path.expanduser(base))
        set_base(base)
        self.md = {'name': 'john', 'age': 52}
        self.df = pd.DataFrame([[1, 2, 3], [3, 2, 1]], columns=['a', 'b', 'c'])
        self.nparr = np.array([[1, 2, 3], [4, 5, 6]])

    def test_primary_csv(self):
        expt = 'expt1'
        store_data(expt, self.df, self.md, format='csv')
        md, df = retrieve_data(expt)
        self.assertTrue(df.equals(self.df))

    def test_primary_feather(self):
        expt = 'expt2'
        store_data(expt, self.df, self.md)
        md, df = retrieve_data(expt)
        self.assertTrue(df.equals(self.df))

    def test_primary_nump(self):
        expt = 'expt3'
        store_data(expt, self.nparr, self.md)
        md, data = retrieve_data(expt)
        self.assertTrue(np.array_equal(self.nparr, data))

    def test_secondary(self):
        expt = 'expt5'
        fname = os.path.join(expt, 'foo')
        store_data(expt, self.df, self.md)
        df1 = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=['a', 'b', 'c'])
        store_data(fname, df1, format='csv')
        df2 = retrieve_data(fname)
        self.assertTrue(df2.equals(df1))
        md, df3 = retrieve_data(expt)
        self.assertTrue(df3.equals(self.df))

    def test_primary_bad_format(self):
        expt = 'expt6'
        with self.assertRaises(ValueError, msg='data of type str not accepted'):
            store_data(expt, "hello", self.md, format='csv')


# if __name__ == "__main__":
#     main()
