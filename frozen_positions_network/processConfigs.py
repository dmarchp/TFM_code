"""
This program is intended to process the quenched ("frozen positions") spatial configuration files or contact files,
i.e. to extract raw data such as 
degrees, community sizes (w/wo giant component) and store it in a file for later use
"""
import glob
import os
import pandas as pd
import sys
import numpy as np
from subprocess import call
sys.path.append('../')
from package_global_functions import *
from filesHandling_quenched import *


def getDegreesAllConfigs(N, arena_r, interac_r, exclusion_r, push=False):
    pushFolder = 'configs_w_push' if push else 'configs_wo_push'
    path = getExternalSSDpath() + f'/quenched_configs/{N}_bots/{pushFolder}'
    existingConfigs = len(glob.glob(path + '/' + configsFilename(arena_r, exclusion_r)))
    existingContacts = len(glob.glob(path + '/' + contactsFilename(arena_r, exclusion_r, interac_r)))
    print(f'There are {existingConfigs} position files and {existingContacts} contact files for N={N}, ra = {arena_r}, re = {exclusion_r}, ri = {interac_r}, push = {push}.')
    allDegrees = []
    for i in range(1, existingContacts+1):
        filename = contactsFilename(arena_r, exclusion_r, interac_r, i)
        try:
            df = pd.read_csv(path + '/' + filename, sep='\s+', header=None)
            _, degrees = getConfigDegrees(df, N, 1)
        except pd.errors.EmptyDataError:
            print(f'here for i={i}')
            input('enter ')
            degrees = []
        allDegrees.extend(degrees)
    df = pd.DataFrame({'degrees':allDegrees})
    path = getExternalSSDpath() + f'/quenched_configs/{N}_bots/raw_data'
    call(f'mkdir -p {path}', shell=True)
    pushLabel = 'push' if push else 'nopush'
    filename = path + f'/degrees_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet'
    df.to_parquet(filename, index=False)
    
def getComSizesAllConfigs(N, arena_r, interac_r, exclusion_r, push=False, contactsToUse=False, replace = False):
    '''
    configsToUse == False, then use all available.
    '''
    pushFolder = 'configs_w_push' if push else 'configs_wo_push'
    pushLabel = 'push' if push else 'nopush'
    path = getConfigsPath(N) + f'/{pushFolder}'
    rawDataPath = getConfigsPath(N) + '/raw_data'
    existingConfigs = len(glob.glob(path + '/' + configsFilename(arena_r, exclusion_r)))
    existingContacts = len(glob.glob(path + '/' + contactsFilename(arena_r, exclusion_r, interac_r)))
    # check if file already exists and avoid repeating it:
    if (os.path.exists(rawDataPath + f'/comSizes_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet') and not replace):
        print(f'Exiting community sizes computing. N={N}, ra = {arena_r}, re = {exclusion_r}, ri = {interac_r} , push = {push}.')
        print(f'There are {existingConfigs} position files and {existingContacts} contact files.')
        return
    print(f'There are {existingConfigs} position files and {existingContacts} contact files for N={N}, ra = {arena_r}, re = {exclusion_r}, ri = {interac_r} , push = {push}.')
    #input('enter ')
    if contactsToUse:
        existingContacts = contactsToUse if existingContacts > contactsToUse else existingContacts
    comSizesDic = {'configID':[], 'comSizes':[]}
    comSizesWoGcDic = {'configID':[], 'comSizes':[]}
    giantCompsDic = {'configID':[], 'comSizes':[]}
    for i in range(1,existingContacts+1):
        try:
            df = pd.read_csv(path + '/' + contactsFilename(arena_r, exclusion_r, interac_r, i), sep='\s+', header=None)
            comSizes, comSizes_woGC, gc = getConfigComSizes(df, N)
        except pd.errors.EmptyDataError:
            # print(contactsFilename(arena_r, exclusion_r, interac_r, i))
            # input('enter ')
            comSizes, comSizes_woGC, gc = [0,], [0,], 0
        comSizesDic['configID'].extend([i]*len(comSizes)), comSizesDic['comSizes'].extend(comSizes)
        comSizesWoGcDic['configID'].extend([i]*len(comSizes_woGC)), comSizesWoGcDic['comSizes'].extend(comSizes_woGC)
        giantCompsDic['configID'].append(i), giantCompsDic['comSizes'].append(gc)
    dfComSizes, dfComSizesWoGc, dfGiantComps = pd.DataFrame(comSizesDic), pd.DataFrame(comSizesWoGcDic), pd.DataFrame(giantCompsDic)
    call(f"mkdir -p {rawDataPath}", shell=True)
    dfComSizes.to_parquet(rawDataPath + f'/comSizes_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet')
    dfComSizesWoGc.to_parquet(rawDataPath + f'/comSizesWoGc_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet')
    dfGiantComps.to_parquet(rawDataPath + f'/comSizes_of_Gc_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet')
    

if __name__ == '__main__':
    # for ir in np.linspace(3.5,12,18):
    #    getDegreesAllConfigs(35, 20.0, ir, 1.5)
    # for N in [50, 60, 70, 80]:
    #     irs = availableIrs(N, 20.0, 1.5, 0)
    #     for ir in irs:
    #         getComSizesAllConfigs(N, 20.0, ir, 1.5)
    # irs = availableIrs(633, 75.0, 1.5, 0)
    # for ir in irs:
    #     getComSizesAllConfigs(633, 75.0, ir, 1.5, replace=True)
    getComSizesAllConfigs(492, 75.0, 4.5, 1.5)