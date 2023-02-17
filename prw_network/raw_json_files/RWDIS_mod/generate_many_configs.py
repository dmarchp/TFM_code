import pandas as pd
from random import seed, randint
import json
from subprocess import call
import glob

call('mkdir -p configs', shell=True)

inSeed = 3123000
Nconfigs = 25
arena_r = 18.5 # per el moment això no canvia (el canvi s'hauria de fer al codi, no al json)
timeStep = 0.0103
simulationTime = 900

nBots = 35
speed = 9
speedVariation = 2

# discard initial configurations: (400 seconds for N=492)
secondsToDiscard = 50.0
ticksPerSecond = 31.0
ticksToDiscard = secondsToDiscard*ticksPerSecond
print(ticksToDiscard)

filenameRoot = f'PRW_nBots_{nBots}_ar_{arena_r}_speed_{speed}_speedVar_{speedVariation}'
existingConfigs = len(glob.glob('configs/' + filenameRoot + '_*.csv'))

# MODIFY THE JSON FILE
with open(f'kilombo.json', 'r') as f:
    data = json.loads(f.read())
        
data['nBots'] = nBots
data['speed'] = speed
data['speedVariation'] = speedVariation
data['timestep'] = timeStep
data['simulationTime'] = simulationTime
data['formation'] = "random" # options are: "random", "pile", "line", "circle", "ellipse"

if data['GUI'] == 1:
    data['GUI'] = 0

with open('kilombo.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
    
def traj_json_to_csv(filename, ticksToDiscard=0):
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
    


for i in range(Nconfigs):
    seed = randint(0,1000000)
    with open('kilombo.json', 'r') as f:
        data = json.loads(f.read())
    data['randSeed'] = seed
    data['stateFileName'] = filenameRoot + f'_{str(existingConfigs+i+1).zfill(3)}.json'
    with open('kilombo.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    call('./prw', shell=True)
    traj_json_to_csv(data['stateFileName'], ticksToDiscard=ticksToDiscard)
    #call(f"rm {data['stateFileName']}", shell=True)
    #call(f"mv {filenameRoot+ f'_{str(existingConfigs+i+1).zfill(3)}}.csv' configs", shell=True)
    call(f"mv {filenameRoot}{f'_{str(existingConfigs+i+1).zfill(3)}.csv'} configs", shell=True)
    call(f"mv {filenameRoot}{f'_{str(existingConfigs+i+1).zfill(3)}.parquet'} configs", shell=True)
    
    
# once finished, remove the json files:
call(f"rm {filenameRoot}_*.json", shell=True)
