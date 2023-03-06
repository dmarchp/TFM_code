"""
This program is intended to process the quenched ("frozen positions") spatial configuration files or contact files,
i.e. to extract raw data such as 
degrees, community sizes (w/wo giant component) and store it in a file for later use
"""
import glob
import pandas as pd
import sys
from subprocess import call
sys.path.append('../')
from package_global_functions import *

def configsFilename(arena_r, exclusion_r, configID=None):
    """
    if configID is a number returns the filename of the specific file
    if left unspecified returns the wildcard with _*_ instead of e.g. _001_
    """
    if configID:
        return f'bots_xy_positions_{str(configID).zfill(3)}_ar_{arena_r}_er_{exclusion_r}.txt'
    else:
        return f'bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'
    return

def contactsFilename(arena_r, exclusion_r, interac_r, configID=None):
    """
    if configID is a number returns the filename of the specific file
    if left unspecified returns the wildcard with _*_ instead of e.g. _001_
    """
    if configID:
        return f'contact_list_{str(configID).zfill(3)}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'
    else:
        return f'contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'

def getDegreesAllConfigs(N, arena_r, interac_r, exclusion_r, push=False):
    pushFolder = 'configs_w_push' if push else 'configs_wo_push'
    path = getExternalSSDpath() + f'/quenched_configs/{N}_bots/{pushFolder}'
    existingConfigs = len(glob.glob(path + '/' + configsFilename(arena_r, exclusion_r)))
    existingContacts = len(glob.glob(path + '/' + contactsFilename(arena_r, exclusion_r, interac_r)))
    print(f'There are {existingConfigs} position files and {existingConfigs} contact files for N={N}, ra = {arena_r}, re = {exclusion_r}, ri = {interac_r} , push = {push}.')
    allDegrees = []
    for i in range(1, existingContacts+1):
        filename = contactsFilename(arena_r, exclusion_r, interac_r, i)
        df = pd.read_csv(path + '/' + filename, sep='\s+',header=None)
        _, degrees = getConfigDegrees(df, N, 1)
        allDegrees.extend(degrees)
    df = pd.DataFrame({'degrees':allDegrees})
    path = getExternalSSDpath() + f'/quenched_configs/{N}_bots/raw_data'
    call(f'mkdir -p {path}', shell=True)
    pushLabel = 'push' if push else 'nopush'
    filename = path + f'/degrees_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet'
    df.to_parquet(filename, index=False)

if __name__ == '__main__':
    getDegreesAllConfigs(35, 20.0, 8.0, 1.5)
