import pandas as pd

def to_csv(fpath):
    df = pd.read_feather(fpath + '.feather')
    # df.to_csv(fpath+'.csv.gz', index=False, float_format='%.11g')
    df.to_csv(fpath+'.csv', index=False, float_format='%.11g')

if __name__ == '__main__':
    # fpath = '../data/expt/bf/tracked'
    fpath = '../data/expt/or/tracked'
    to_csv(fpath)
