"""
This program includes analysis functions to study percolation in quenched configs:
degree distribution, community sizes distibution, mean cluster size...
uses the N_bots/raw_data/ files...
"""
import glob
import os
import pandas as pd
import sys
from subprocess import call
sys.path.append('../')
from package_global_functions import *
from filesHandling_quenched import *

# MEAN CLUSTER SIZE
def computeMeanClusterSize(N, arena_r, interac_r, exclusion_r, push, maxConfigs):
    """
    computes the mean cluster size for specific conditions: N, ar, ir, er...
    """
    pushLabel = 'push' if push else 'nopush'
    path = getConfigsPath(N)
    rawDataFilename = path + f'/raw_data/comSizesWoGc_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet'
    df = pd.read_parquet(rawDataFilename)
    configs = list(pd.unique(df['configID']))
    if max(configs) > maxConfigs:
        # from 1 to maxConfig:
        configsToUse = configs[:maxConfigs+1]
        # or randomly select maxConfigs:
        # configsToUse = sample(configsToUse, k=maxConfigs)
        # configsToUse.sort()
    else:
        configsToUse = configs
    dfaux = df.query('configID in @configsToUse').copy()
    dfaux['comSizes_sq'] = dfaux['comSizes']**2
    a = sum(dfaux['comSizes'])
    b = sum(dfaux['comSizes_sq'])
    try:
        mcs = b/a
    except ZeroDivisionError:
        mcs = float('nan')
    return mcs
    
def getMeanClusterSize_ir(N, arena_r, exclusion_r, irs, push=False, maxConfigs=False):
    """
    gets the MCS along a set of interaction radius, for fixed N, ar, er, push
    maxConfigs == False, then use all available
    """
    pushLabel = 'push' if push else 'nopush'
    path = getConfigsPath(N)
    pDataPath, rDataPath = path + '/processed_data', path + '/raw_data'
    if not maxConfigs:
        df = pd.read_parquet(rDataPath + f'/comSizesWoGc_N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet')
        configLabel = max(list(pd.unique(df['configID'])))
    else:
        configLabel = maxConfigs
    if not os.path.exists(pDataPath):
        call(f'mkdir -p {pDataPath}', shell=True)
    filename = pDataPath + f'/meanClusterSize_{pushLabel}_N_{N}_ar_{arena_r}_er_{exclusion_r}.csv' # _{configLabel}_configs
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        missing_irs = [ir for ir in irs if ir not in list(df['interac_r'])]
        if missing_irs:
            mcs_l = []
            for ir in missing_irs:
                mcs = computeMeanClusterSize(N, arena_r, ir, exclusion_r, push, maxConfigs)
                mcs_l.append(mcs)
            df_missing_irs = pd.DataFrame({'interac_r':missing_irs, 'mcs':mcs_l})
            df = pd.concat([df, df_missing_irs], ignore_index=True)
            df = df.sort_values(by='interac_r')
            df.to_csv(filename, index=False)
    else:
        mcs_l = []
        for ir in irs:
            mcs = computeMeanClusterSize(N, arena_r, ir, exclusion_r, push, maxConfigs)
            mcs_l.append(mcs)
        df = pd.DataFrame({'interac_r':irs, 'mcs':mcs_l})
        df.to_csv(filename, index=False)
    return df



# Average giant component:

def computeAvgGiantComp(N, arena_r, interac_r, exclusion_r, push, maxConfigs):
    """
    computes the mean cluster size for specific conditions: N, ar, ir, er...
    """
    pushLabel = 'push' if push else 'nopush'
    path = getConfigsPath(N)
    rawDataFilename = path + f'/raw_data/comSizes_of_Gc_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet'
    df = pd.read_parquet(rawDataFilename)
    configs = list(pd.unique(df['configID']))
    if max(configs) > maxConfigs:
        configsToUse = configs[:maxConfigs+1]
    else:
        configsToUse = configs
    df = df.query('configID in @configsToUse').copy()
    return df['comSizes'].mean(), df['comSizes'].std()


def getAvgGiantComp_ir(N, arena_r, exclusion_r, irs, push=False, maxConfigs=False):
    """
    gets the average giant component along a set of interaction radius, for fixed N, ar, er, push
    maxConfigs == False, then use all available
    """
    pushLabel = 'push' if push else 'nopush'
    path = getConfigsPath(N)
    pDataPath, rDataPath = path + '/processed_data', path + '/raw_data'
    if not os.path.exists(pDataPath):
        call(f'mkdir -p {pDataPath}', shell=True)
    filename = pDataPath + f'/avgGiantComp_{pushLabel}_N_{N}_ar_{arena_r}_er_{exclusion_r}.csv' # _{configLabel}_configs
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        missing_irs = [ir for ir in irs if ir not in list(df['interac_r'])]
        if missing_irs:
            avgs, stds = []
            for ir in missing_irs:
                avg, std = computeAvgGiantComp(N, arena_r, ir, exclusion_r, push, maxConfigs)
                avgs.append(avg), stds.append(std)
            df_missing_irs = pd.DataFrame({'interac_r':missing_irs, 'avg':avgs, 'std':stds})
            df = pd.concat([df, df_missing_irs], ignore_index=True)
            df = df.sort_values(by='interac_r')
            df.to_csv(filename, index=False)
    else:
        avgs, stds = [], []
        for ir in irs:
            avg, std = computeAvgGiantComp(N, arena_r, ir, exclusion_r, push, maxConfigs)
            avgs.append(avg), stds.append(std)
        df = pd.DataFrame({'interac_r':irs, 'avg':avgs, 'std':stds})
        df.to_csv(filename, index=False)
    return df
    
if __name__ == '__main__':
    # N, ar, er = 35, 20.0, 1.5
    N, ar, er = 492, 75.0, 1.5
    irs = availableIrs(N, ar, er, push=False)
    #print(irs)
    # per 492 que n'hagi generat les llistes de comsizes
    irs = [3.5, 4.0, 5.0, 5.5, 6.0, 6.3, 6.4, 6.5, 6.6, 6.7, 7.0, 7.5, 8.0, 9.0, 10.0]
    # getMeanClusterSize_ir(N, ar, er, irs, maxConfigs=1000) # maxConfigs 144 for N=492, 1000 for N=35
    getAvgGiantComp_ir(N, ar, er, irs, maxConfigs=1000)



