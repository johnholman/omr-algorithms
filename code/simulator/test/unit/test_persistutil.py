import os
import unittest

import numpy as np
import pandas as pd

from simulator.sessrun.md import MD
from simulator.sessrun.persist import set_base
# def put_data(df, metadata=None, *, filename=None, expt_name=None, format=None):
from simulator.sessrun.util import save_data, load_data


class Test(unittest.TestCase):

    def setUp(self):
        base = r'~\temp\data\persist_tests'
        base = os.path.normpath(os.path.expanduser(base))
        set_base(base)
        self.md = {'name': 'john', 'age': 52}
        self.mdobj = MD(self.md)
        self.pdf = pd.DataFrame([[1, 2, 3], [3, 2, 1]], columns=['a', 'b', 'c'])
        self.nparr = np.array([[1, 2, 3], [4, 5, 6]])
        self.sdf = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=['x', 'y', 'z'])

    def test_primary_default(self):
        save_data(self.pdf, metadata=self.md, format='csv')
        md, df = load_data()
        self.assertTrue(df.equals(self.pdf))
        self.assertEqual(md.md, self.mdobj.md)

    def test_secondary_default(self):
        save_data(self.sdf, filename='f1', format='csv')
        df = load_data('f1')
        self.assertTrue(df.equals(self.sdf))

    def test_primary_expt_specified(self):
        save_data(self.pdf, metadata=self.md, expt_name='pu1', format='csv')
        md, df = load_data(expt_name='pu1')
        self.assertTrue(df.equals(self.pdf))
        self.assertEqual(md.md, self.mdobj.md)

    def test_secondary_expt_specified(self):
        save_data(self.sdf, filename='f1', expt_name='pu1', format='csv')
        df = load_data('f1', expt_name='pu1')
        self.assertTrue(df.equals(self.sdf))

    def test_primary_folder_specified(self):
        save_data(self.pdf, metadata=self.md, expt_name='pu1', project_name='myproj', format='csv')
        md, df = load_data(expt_name='pu1', project_name='myproj')
        self.assertTrue(df.equals(self.pdf))
        self.assertEqual(md.md, self.mdobj.md)

    def test_secondary_folder_specified(self):
        save_data(self.sdf, filename='f1', project_name='myproj', expt_name='pu1', format='csv')
        df = load_data('f1', project_name='myproj', expt_name='pu1')
        self.assertTrue(df.equals(self.sdf))

    # def test_primary_feather(self):
    #     expt = 'expt2'
    #     save_data(expt, self.df, self.md)
    #     md, df = load_data(expt)
    #     self.assertTrue(df.equals(self.df))
    #
    # def test_primary_nump(self):
    #     expt = 'expt3'
    #     save_data(expt, self.nparr, self.md)
    #     md, data = load_data(expt)
    #     self.assertTrue(np.array_equal(self.nparr, data))
    #
    # def test_secondary_without_folder(self):
    #     expt = r'expt4\foo'
    #     with self.assertRaises(Exception):
    #         save_data(expt, self.df, format='csv')
    #
    # def test_secondary(self):
    #     expt = 'expt5'
    #     fname = os.path.join(expt, 'foo')
    #     save_data(expt, self.df, self.md)
    #     df1 = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=['a', 'b', 'c'])
    #     save_data(fname, df1, format='csv')
    #     df2 = load_data(fname)
    #     self.assertTrue(df2.equals(df1))
    #     md, df3 = load_data(expt)
    #     self.assertTrue(df3.equals(self.df))
    #
    # def test_primary_bad_format(self):
    #     expt = 'expt6'
    #     with self.assertRaises(ValueError):
    #         save_data(expt, "hello", self.md, format='csv')


if __name__ == "__main__":
    unittest.main()
