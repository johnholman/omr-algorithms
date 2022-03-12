import os
import time
import pandas as pd

def load_tracked_data(indir):
    ''' Return dataframe containing free swimming data from given directory
    
    Expected format: 
    directory for each condition named <h>_<s> where h is the height and s is 
    the stimulus speed, e.g. h1_4
    
    within the condition directory a CSV file for each fish experiencing this condition,
    named fish<n>.csv where <n> is the fish number, e.g. fish48.csv
    
    The returned dataframe has columns height, stimulus_speed, id, time, xpos, ypos
    '''

    indir = os.path.expanduser(indir)

    print(f'source directory: {indir}')

    dflist = []
    for groupdir in os.listdir(indir):
        print(f'groupdir {groupdir}')
        df = group_data(os.path.join(indir, groupdir))
        dflist.append(df)
    df = pd.concat(dflist, ignore_index = True)
    return df        
        
def group_data(conddir):
    ''' Return dataframe containing data for a single experimental condition in
    the given directory
    '''
    dflist = []
    for fish_file in os.listdir(conddir):
        dpath = os.path.join(conddir, fish_file)
        dflist.append(fish_data(dpath))
    df = pd.concat(dflist, ignore_index = True)
    return df
        
def fish_data(dpath):
    ''' Return dataframe containing data for a single fish and experimental condition for
    the given CSV file 
    '''
    # height and stimulus speed encoded in the directory and filename
    gname = os.path.basename(os.path.dirname(dpath))
    height, ss = gname.split('_')

    # subject id encoded in the filename
    dname, _ = os.path.splitext(os.path.basename(dpath))
    prefix = 'fish'
    if dname.startswith(prefix):
        subj_id = dname[len(prefix):]
    else:
        raise Exception(f'expected {prefix} as filename prefix')
    
    print(f'reading track file {dpath} height {height} stimspeed {ss} id {subj_id}')
    df = pd.read_csv(dpath, names=['time', 'xpos', 'ypos'])

    df['id'] = int(subj_id)
    df['height']=height
    df['stimulus_speed']=float(ss)
    df = df[['height', 'stimulus_speed', 'id', 'time', 'xpos', 'ypos']]

    return df

def save_data(df, dirpath, fname):
    df.head()
    _, ext = os.path.splitext(fname)
    outpath = os.path.join(dirpath, fname)
    print(f'saving to {outpath} as {ext}')
    if ext == '.csv':
        df.to_csv(outpath, )
    elif ext == '.feather':
        df.info()
        df.to_feather(outpath)
    else:
        raise ValueError(f'unrecognized extension {ext}')

if __name__ == '__main__':

    indir=r'~\Google Drive\data\ezfish\freeswim\tracked_data_for_pilot'
    outdir=r'~\data\ezfish\freeswim\pilot\temp'
    outfile = 'fsm_track.feather'
    # outfile = 'fsm_track.csv'

    start = time.time()

    df = load_tracked_data(indir)
    save_data(df, outdir, outfile)

    print(f'Elapsed time {time.time()-start :.1f}')

