import os
import glob
import pandas as pd
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
    
    
# FILE COUNTING:

def countConfigs(N, arena_r, speed = 9, speedVar = 2):
    fullNameWc = getConfigsPath() + '/' + getFilenameRoot(N,arena_r,speed,speedVar) + '_*' + getFilesExtension()
    c = len(glob.glob(fullNameWc))
    return c
    
def countContacts(N, arena_r, interac_r, loops, speed = 9, speedVar = 2):
    fullNameWc = getConfigsPath() + '/contacts/' + getFilenameRoot(N,arena_r,speed,speedVar) + '_*'
    fullNameContactWc = fullNameWc + getFilenameContactSufix(loops, interac_r)
    fullNameContactIntWc = fullNameWc + getFilenameContactIntSufix(loops, interac_r)
    c, ci = len(glob.glob(fullNameContactWc)), len(glob.glob(fullNameContactIntWc))
    return c, ci
    
def countContactConfigs(N, arena_r, interac_r, loops, speed = 9, speedVar = 2):
    nContactFiles, _ = countContacts(N, arena_r, interac_r, loops, speed, speedVar)
    for i in range(1,nContactFiles+1):
        fname = getConfigsPath() + '/contacts/' + getFilenameRoot(N,arena_r,speed,speedVar)
        fname += getFilenameNumber(i) + getFilenameContactSufix(loops, interac_r)
        df = pd.read_parquet(fname)
        configs, cicles = len(pd.unique(df['configID'])), len(pd.unique(df['cicleID']))
        print(configs, cicles)
        
def countContactIntConfigs(N, arena_r, interac_r, loops, speed = 9, speedVar = 2):
    _, nContactIntFiles = countContacts(N, arena_r, interac_r, loops, speed, speedVar)
    counter = 0
    ciclesEachConfig = []
    for i in range(1,nContactIntFiles+1):
        fname = getConfigsPath() + '/contacts/' + getFilenameRoot(N,arena_r,speed,speedVar)
        fname += getFilenameNumber(i) + getFilenameContactIntSufix(loops, interac_r)
        df = pd.read_parquet(fname)
        cicles = len(pd.unique(df['cicleID']))
        counter += cicles
        ciclesEachConfig.append(cicles)
    return counter, ciclesEachConfig
        
        
# mes que mirar contact list hauria de mirar quins tenen els com sizes calculats...
def availableIrs(N, arena_r, loops, speed = 9, speedVar = 2):
    fullNameWc = getConfigsPath() + '/contacts/' + getFilenameRoot(N,arena_r,speed,speedVar) + '_*'
    fullNameWc += f'_loops_{loops}_ir_*_contacts.parquet'
    files = glob.glob(fullNameWc)
    irs = []
    for f in files:
        ir = float(f.split('_')[14])
        if ir not in irs:
            irs.append(ir)
    irs.sort()
    return irs
        

