"""
This program is intended to process the kilombo spatial configuration files or contact files,
i.e. to extract raw data such as 
degrees, community sizes (w/wo giant component) and store it in a file for later use
"""
import pandas as pd
import glob
import os
from subprocess import call
import sys
sys.path.append('../')
from package_global_functions import *
from filesHandling_kilombo import getFilenameRoot, getFilenameContactIntSufix, getConfigsPath

# to do:
# community sizes from all traj, w/wo giant component
# giant component sizes

def getDegreesAllTraj(N, arena_r, interac_r, loops):
    fname = getFilenameRoot(N, arena_r) # speed and speedVar are default. If they were ever to change, arguments in the function detDegreesAllTraj should be added
    fnameSufix = getFilenameContactIntSufix(loops, interac_r)
    contactsPath = getConfigsPath() + '/contacts'
    existingFiles = len(glob.glob(contactsPath + '/' + fname + '_*' + fnameSufix))
    # print(existingFiles)
    call(f"mkdir -p {getConfigsPath()}/raw_data", shell=True)
    allDegrees = []
    for i in range(1,existingFiles+1):
        df = pd.read_parquet(contactsPath + '/' + fname + f'_{str(i).zfill(3)}' + fnameSufix)
        cicles = pd.unique(df['cicleID'])
        for cicle in cicles:
            dfcicle = df.query('cicleID == @cicle')
            dfcicle = dfcicle.drop('cicleID', axis=1)
            _, degrees = getConfigDegrees(dfcicle, N, firstID=0)
            allDegrees.extend(degrees)
    dfdegrees = pd.DataFrame({'degrees':allDegrees})
    dfdegrees.to_parquet(f'{getConfigsPath()}/raw_data/degrees_N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet', index=False)

if __name__ == '__main__':
    getDegreesAllTraj(35, 18.5, 7.0, 800)