import glob
import sys
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
        
        
def getConfigsPath(N):
    ssdPath = getExternalSSDpath()
    if os.path.exists(ssdPath):
        configsPath = ssdPath + f'/quenched_configs/{N}_bots'
    else:
        configsPath = f'frozen_positions_new/positions_and_contacts/{N}_bots'
    return configsPath
    
    
def availableIrs(N, arena_r, exclusion_r, push):
    pushFolder = '/configs_w_push' if push else '/configs_wo_push'
    fullNameWc = getConfigsPath(N) + pushFolder + f'/contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_*.txt'
    files = glob.glob(fullNameWc)
    irs = []
    for f in files:
        ir = float(f.split('_')[12][:-4]) # aixo nomes funciona si esta el ssd
        if ir not in irs:
            irs.append(ir)
    irs.sort()
    return irs
