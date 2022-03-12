import pandas as pd

from simulator.sessrun.util import load_data, save_data


class ResultsCache:
    def __init__(self, keynames, *, expt_name=None, project_name=None, filename='resultscache', precision=8):
        self.keynames = tuple(var if var.endswith('_grid') else var + '_grid' for var in keynames)
        self.expt_name = expt_name
        self.project_name = project_name
        self.filename = filename
        self.olddf = None  # most recently loaded version
        self.newdf = None  # most recently saved version
        self.cache = {}
        self.precision = precision

    def round(self, values):
        return tuple(round(val, self.precision) for val in values)

    def __contains__(self, key):
        if isinstance(key, dict):
            key = tuple(key.values())
        if len(key) != len(self.keynames):
            raise ValueError(f'key values for cache items should be of length {len(self.keynames)}')
        return self.round(key) in self.cache

    def __getitem__(self, key):
        if isinstance(key, dict):
            key = tuple(key.values())
        if len(key) != len(self.keynames):
            raise ValueError(f'key values for cache items should be of length {len(self.keynames)}')
        return self.cache[self.round(key)]

    def __setitem__(self, key, value):
        if isinstance(key, dict):
            key = tuple(key.values())
        if len(key) != len(self.keynames):
            raise ValueError(f'key values for cache items should be of length {len(self.keynames)}')
        if not isinstance(value, dict):
            raise ValueError('value for caching must be dictionary')
        for vkey in value.keys():
            if vkey.endswith('_grid'):
                raise ValueError(f'invalid result key {key}')
        self.cache[self.round(key)] = value

    def __len__(self):
        return len(self.cache)

    def clear(self):
        self.cache = {}

    def load(self):
        try:
            self.olddf = df = load_data(filename=self.filename, expt_name=self.expt_name,
                                        project_name=self.project_name)
        except Exception:
            return False
        keycols = tuple(col for col in df.columns if col.endswith('_grid'))

        # verify cache file is compatible with the given keynames. An empty cache file is considered OK
        if len(keycols) != 0 and keycols != self.keynames:
            raise ValueError(f'Cache keynames {keycols} differ from expected names {self.keynames} ')

        # don't attempt load if the cache file is empty
        if len(df) == 0:
            return False

        # keys are tuples of values of grid variables, values are dictionaries of error results
        keyvals = df[list(self.keynames)].to_records(index=False)
        resultcols = [col for col in df.columns if not col.endswith('_grid')]
        results = df[resultcols].to_dict(orient='records')
        for keyval, result in zip(keyvals, results):
            self.cache[tuple(keyval)] = result

        return True

    def save(self, *, filename=None):
        if filename is None:
            filename = self.filename

        if len(self.cache) == 0:
            self.newdf = df = pd.DataFrame(columns=self.keynames).reset_index(drop=True)
        else:
            ds = []
            for keyvals, errs in self.cache.items():
                d = {}
                for varname, varval in zip(self.keynames, keyvals):
                    d[varname] = varval
                for errname, errval in errs.items():
                    d[errname] = errval
                ds.append(d)

            self.newdf = df = pd.DataFrame(ds).reset_index(drop=True)

        save_data(df, filename=filename, expt_name=self.expt_name, project_name=self.project_name,
                  format='feather')


def test():
    keynames = 'tau_grid', 'ke_tau_prod_grid', 'sr_tau_prod_grid'
    cache = ResultsCache(keynames, project_name='pub21', expt_name='li_single_sbo_fit_cache')
    if cache.load():
        print('cache loaded from file')
    else:
        print('new cache')
    return cache


if __name__ == '__main__':
    c = test()
