import os
import sys
sys.path.append('../')
from package_global_functions import getExternalSSDpath

def getConfigsPath():
    ssdPath = getExternalSSDpath()
    if os.path.exists(ssdPath):
        configsPath = ssdPath + '/kilombo_configs'
    else:
        configsPath = 'kilombo_config_generator/configs'
    return configsPath

def getFilenameRoot(N, arena_r, speed = 9, speedVar = 2):
    return f'PRW_nBots_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}'
    
def getFilenameNumber(configNumber, zerosFill=3):
    return '_' + str(configNumber).zfill(zerosFill)

def getFilenameContactSufix(loops, interac_r):
    return f'_loops_{loops}_ir_{interac_r}_contacts.parquet'

def getFilenameContactIntSufix(loops, interac_r):
    return f'_loops_{loops}_ir_{interac_r}_contacts_cicleINT.parquet'
    
def getFilesExtension():
    return '.parquet'
