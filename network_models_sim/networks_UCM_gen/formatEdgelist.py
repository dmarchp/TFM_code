import pandas as pd
import glob
import sys
import os
from subprocess import call
sys.path.append('../../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    ucmPath = extSSDpath + getProjectFoldername() + '/network_models_sim/networks_UCM_gen/'
else:
    ucmPath = '/.'


# if __name__ == '__main__':

files = glob.glob('N*_g*_min*_*.dat')

for file in files:
    indexToDelete = []
    df = pd.read_csv(file, names = ['i', 'j'], delimiter=r"\s+")
    df.sort_values(by=['i', 'j'], inplace=True)
    for row in df.itertuples():
        indexFirst, i, j = row[0], row[1], row[2]
        if not df.query('i == @j & j == @i').empty:
            indexSecond = df.query('i == @j & j == @i').index[0]
            if indexSecond > indexFirst:
                indexToDelete.append(indexSecond)
    df.drop(index=indexToDelete, inplace=True)
    df.to_csv(f'{file}', header=False, index=False, sep=' ')

parts = files[0].split('_')
folderName = '_'.join(parts[:-1])
print(folderName)
if not os.path.exists(f'{ucmPath}{folderName}'):
    os.mkdir(f'{ucmPath}{folderName}')
call(f'mv N*_g*_min*_*.dat {ucmPath}{folderName}', shell=True)

# for file in files:
#     df = pd.read_csv(file, names = ['i', 'j'], delimiter=r"\s+")
#     df['i'] = df['i'] - 1
#     df['j'] = df['j'] - 1
#     df.to_csv(f'{file}', header=False, index=False, sep=' ')