import pandas as pd
from random import seed, randint
import json
from subprocess import call
import glob
import os
import sys
sys.path.append('../../')
from package_global_functions import *

# parameters:
inSeed = 600
Nconfigs = 2
arena_r = 73.5 # per el moment això no canvia (el canvi s'hauria de fer al codi, no al json)

# parameters to modify in the kilombo.json
nBots = 492
speed = 9
speedVariation = 2
timeStep = 0.0103
simulationTime = 700
formation = "pile" # options are: "random", "pile", "line", "circle", "ellipse"
# for small sizes (N=35), random is ok
# for a bigger szize (N=492), pile or ellipse produce a better inicial spread. Nvthless, a discarding time of about 400 seconds must be set
# in order to decorrelate from the initial formation

# discard initial configurations: (400 seconds for N=492)
secondsToDiscard = 400.0
ticksPerSecond = 31.0
ticksToDiscard = secondsToDiscard*ticksPerSecond
#print(ticksToDiscard)

#filenameRoot = f'PRW_nBots_{nBots}_ar_{arena_r}_speed_{speed}_speedVar_{speedVariation}'
filenameRoot = getFilenameRoot(nBots, arena_r, speed , speedVariation)
extension = getFilesExtension()
existingConfigs = len(glob.glob('configs/' + filenameRoot + '_*' + extension))

def modify_arena_size_in_PRWDIS():
    global arena_r
    call(f"sed -i 's/  double arena_r = .*/  double arena_r = {round(arena_r*10,2)}/' PRWDis.c", shell=True)
    #call("make", shell=True)
    
def modify_kilombo_json():
    global nBots, speed, speedVariation, timeStep, simulationTime
    with open(f'kilombo.json', 'r') as f:
        data = json.loads(f.read())
    data['nBots'] = nBots
    data['speed'] = speed
    data['speedVariation'] = speedVariation
    data['timestep'] = timeStep
    data['simulationTime'] = simulationTime
    data['formation'] = "pile" 
    if data['GUI'] == 1:
        data['GUI'] = 0
    with open('kilombo.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def traj_json_to_csv_or_parquet(filename, ticksToDiscard=0, csv=False, parquet=True):
    with open(filename, 'r') as f:
        trajJSON = json.loads(f.read())
    trajDF = pd.json_normalize(trajJSON, record_path='bot_states', meta='ticks')
    trajDF.drop('direction', axis=1, inplace=True)
    if(ticksToDiscard):
        trajDF.drop(trajDF[trajDF.ticks < ticksToDiscard].index, inplace=True)
    # set datatypes:
    trajDF['ID'] = trajDF['ID'].astype('int16')
    trajDF['x_position'] = trajDF['x_position'].astype('float32')
    trajDF['y_position'] = trajDF['y_position'].astype('float32')
    trajDF['ticks'] = trajDF['ticks'].astype('int32')
    # sate to CSV or PARQUET... still figuring it out...
    filenameCSV = filename[:-4] + 'csv'
    filenameParquet = filename[:-4] + 'parquet'
    trajDF.to_csv(filenameCSV, index=False)
    trajDF.to_parquet(filenameParquet, index=False)
    

def move_traj_files(saveToExtSDD=True):
    extSSDpath = getExternalSSDpath()
    if os.path.exists(extSSDpath) and saveToExtSDD:
        call(f'mv configs/* {extSSDpath}/kilombo_configs', shell=True)
    elif not os.path.exists(extSSDpath) and saveToExtSSD:
        print('External SDD drive is not available. Leaving cofing trajectories in configs/')
    

def generate_configs(csv=False, parquet=True):
    global Nconfigs, inSeed, filenameRoot, existingConfigs, ticksToDiscard
    call('mkdir -p configs', shell=True)
    seed(inSeed)
    for i in range(Nconfigs):
        kiloSeed = randint(0,1000000)
        with open('kilombo.json', 'r') as f:
            data = json.loads(f.read())
        data['randSeed'] = kiloSeed
        data['stateFileName'] = filenameRoot + f'_{str(existingConfigs+i+1).zfill(3)}.json'
        with open('kilombo.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        call('./prw', shell=True)
        traj_json_to_csv_or_parquet(data['stateFileName'], ticksToDiscard=ticksToDiscard, csv=csv, parquet=parquet)
        if csv:
            call(f"mv {filenameRoot}{f'_{str(existingConfigs+i+1).zfill(3)}.csv'} configs", shell=True)
        if parquet:
            call(f"mv {filenameRoot}{f'_{str(existingConfigs+i+1).zfill(3)}.parquet'} configs", shell=True)
        # once finished, remove the json files:
        call(f"rm {filenameRoot}_*.json", shell=True)
        

def mainComplete():
    modify_arena_size_in_PRWDIS()
    modify_kilombo_json()
    generate_configs()
    move_traj_files()
    
def mainTesting():
    move_traj_files()
    
if __name__ == '__main__':
    #mainComplete()
    mainTesting()
