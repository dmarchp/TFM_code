import pandas as pd
import glob
import os
import re
from subprocess import call
import sys
sys.path.append('../../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    ucmPath = extSSDpath + getProjectFoldername() + '/network_models_sim/networks_UCM_gen/'
else:
    ucmPath = 'networks_UCM_gen/'

# rename wrongly named files:
# filesBad = glob.glob('N*_g*_min*.dat')
# for file in filesBad:
#     idx = file.split('_')[2].replace('.dat', '').replace('min', '')
#     print(idx)
#     correctName = f'N500_g2.0_min2_{idx}.dat'
#     call(f'mv {file} {correctName}', shell=True)

files = glob.glob('N*_g*_min*_*.dat')
print(len(files))

### DELETE DUPLICATE EDGES ###
for i,file in enumerate(files):
    print(f'Working on file {i}: {file}')
    df = pd.read_csv(file, names=['i', 'j'], delimiter=r'\s+')
    df.sort_values(by=['i', 'j'], inplace=True)
    idxsToDelete = []
    for row in df.itertuples():
        idx, i, j = row[0], row[1], row[2]
        dfaux = df.query('i == @j and j == @i')
        if not dfaux.empty:
            idxDelete = dfaux.index[0]
            if idxDelete > idx:
                idxsToDelete.append(idxDelete)
    df.drop(idxsToDelete, inplace=True)
    df.to_csv(file, index=False, sep=' ', header=False)
    # idx = file.split('_')[3].replace('.dat','')
    # df.to_csv(f'N500_g2.0_min1_{idx}.dat', index=False, sep=' ', header=False)
    


### MOVE FILES TO SSD ###
folderName = re.sub('_[0-9]+.dat', '', files[0])
print(folderName)
# input('enter ')
if not os.path.exists(f'{ucmPath}{folderName}'):
    call(f'mkdir {ucmPath}{folderName}', shell=True)
call(f'mv N*_g*_min*_*.dat {ucmPath}{folderName}', shell=True)

        
    