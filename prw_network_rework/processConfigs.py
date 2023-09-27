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
from filesHandling_kilombo import getFilenameRoot, getFilenameContactIntSufix, getConfigsPath, availableIrs

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


def getComSizesAllTraj(N, arena_r, interac_r, loops, maxCicles=False):
    fname = getFilenameRoot(N, arena_r)
    fnameSufix = getFilenameContactIntSufix(loops, interac_r)
    contactsPath = getConfigsPath() + '/contacts'
    existingFiles = len(glob.glob(contactsPath + '/' + fname + '_*' + fnameSufix))
    call(f"mkdir -p {getConfigsPath()}/raw_data", shell=True)
    comSizesDic = {'trajID':[], 'cicleID':[], 'comSizes':[]}
    comSizesWoGcDic = {'trajID':[], 'cicleID':[], 'comSizes':[]}
    giantCompsDic = {'trajID':[], 'cicleID':[], 'comSizes':[]}
    for i in range(1,existingFiles+1):
        df = pd.read_parquet(contactsPath + '/' + fname + f'_{str(i).zfill(3)}' + fnameSufix)
        cicles = pd.unique(df['cicleID'])
        minCicleID, maxCicleID = min(cicles), max(cicles)
        if not 0 in cicles: # això es per comprovar que els he canviat tots bé; en un futur es podrà treure
            print(f'Config {i} first cicle is labeled {minCicleID}!')
        if maxCicles:
            if max(cicles) < maxCicles:
                print(f'{maxCicles} cicles were to be used for each trajectory but there are only {len(cicles)} cicles in traj {i}.')
            else:
                df = df.query('cicleID < @maxCicles') # assuming they are labelled starting by ID=0
                cicles = pd.unique(df['cicleID'])
        for cicle in cicles:
            dfcicle = df.query('cicleID == @cicle')
            dfcicle = dfcicle.drop('cicleID', axis=1)
            comSizes, comSizes_woGC, gc = getConfigComSizes(dfcicle, N)
            comSizesDic['trajID'].extend([i]*len(comSizes)), comSizesDic['cicleID'].extend([cicle]*len(comSizes)), comSizesDic['comSizes'].extend(comSizes)
            comSizesWoGcDic['trajID'].extend([i]*len(comSizes_woGC)), comSizesWoGcDic['cicleID'].extend([cicle]*len(comSizes_woGC)), comSizesWoGcDic['comSizes'].extend(comSizes_woGC)
            giantCompsDic['trajID'].append(i), giantCompsDic['cicleID'].append(cicle), giantCompsDic['comSizes'].append(gc)
    dfComSizes, dfComSizesWoGc, dfGiantComps = pd.DataFrame(comSizesDic), pd.DataFrame(comSizesWoGcDic), pd.DataFrame(giantCompsDic)
    dfComSizes.to_parquet(f'{getConfigsPath()}/raw_data/comSizes_N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet', index=False)
    dfComSizesWoGc.to_parquet(f'{getConfigsPath()}/raw_data/comSizesWoGc_N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet', index=False)
    dfGiantComps.to_parquet(f'{getConfigsPath()}/raw_data/comSizes_of_Gc__N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet', index=False)



if __name__ == '__main__':
    # getDegreesAllTraj(35, 18.5, 7.0, 800)
    N, ar, loops = 35, 18.5, 800
    # for loops in [400, 800]:
    #     irs = availableIrs(N, ar, loops)
    #     for ir in irs:
    #         getComSizesAllTraj(N, ar, ir, loops)
    for N in [40, 45]:
        getComSizesAllTraj(N, ar, 3.4, loops)
