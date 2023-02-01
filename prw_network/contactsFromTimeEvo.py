import pandas as pd
from collections import Counter
import glob
from tqdm import tqdm
import numpy as np
from subprocess import call
import os
from time import time
import multiprocessing as mp

arena_r = 75.0 # centimeters
exclusion_r = 1.5 # centimeters
interac_r = 80.0 # milimeters

timestep = 0.0103 # seconds per loop
ticksPerSecond = 31
ticksPerLoop = timestep*ticksPerSecond
loops = 800

N = 492
speed = 9
speedVar = 2

configs_path = 'raw_json_files/RWDIS_mod/configs/'


def dist2D(pos0, pos1):
    return np.sqrt((pos0[0]-pos1[0])**2+(pos0[1]-pos1[1])**2)
    
def getContactsFromCicle(df, cID, ids, ticksPerCicle):
    global interac_r
    configID, cicleID, contacts0, contacts1 = [], [], [], []
    df.reset_index(drop=True, inplace=True)
    if (loops == 0):
        cicle = df['ticks'][0]/3 # ticks 3 es la separació en ticks de les configs. Hard Coded, Lleig.
    else:
        cicle = int(df['ticks'][0]/ticksPerCicle)
    for j,id0 in enumerate(ids[:-1]):
        pos0 = (df['x_position'][j], df['y_position'][j])
        for k,id1 in enumerate(ids[j+1:]):
            pos1 = (df['x_position'][k+j+1], df['y_position'][k+j+1])
            dist = dist2D(pos0, pos1)
            if(dist<interac_r):
               configID.append(cID), cicleID.append(cicle), contacts0.append(id0), contacts1.append(id1)
    return configID, cicleID, contacts0, contacts1

def getContactsFromTraj(filename, interac_r, loops, toFile=True):
    ticksPerCicle = loops*ticksPerLoop
    trajDF = pd.read_csv(configs_path+filename)
    # get a contact list from each configuration:
    ids = pd.unique(trajDF['ID'])
    Nbots = len(ids)
    Nconfigs = len(trajDF)/Nbots
    # is there any tick with more than 1 config?
    count = Counter(list(trajDF.loc[trajDF['ID']==0]['ticks']))
    ticks_plus1_configs = []
    for k,v in count.items():
        if v>1:
            ticks_plus1_configs.append(k)
    if(ticks_plus1_configs):
        print(f"There are {len(ticks_plus1_configs)} ticks with more than 1 config, from Nconfigs.")
    # search for contacts in each configuration and build the columns of a future dataframe:
    configID, cicleID, contacts0, contacts1 = [], [], [], []
    # keep in mind that if an initial time is discarded when generating the Traj, cicle=0 corresponds to a mid simulation time already
    cicle = 0
    for i in tqdm(range(int(Nconfigs))):
        dfconfig = trajDF.loc[(i*Nbots):(i*Nbots+Nbots-1)]
        dfconfig.reset_index(drop=True, inplace=True)
        if int(dfconfig['ticks'][0]) > (cicle+1)*ticksPerCicle:
            cicle += 1
        for j,id0 in enumerate(ids[:-1]):
            pos0 = (dfconfig['x_position'][j], dfconfig['y_position'][j])
            for k,id1 in enumerate(ids[j+1:]):
                pos1 = (dfconfig['x_position'][k+j+1], dfconfig['y_position'][k+j+1])
                dist = dist2D(pos0, pos1)
                if(dist<interac_r):
                    configID.append(i), cicleID.append(cicle), contacts0.append(id0), contacts1.append(id1)
    # build the dataframe:
    dfconfigs = pd.DataFrame({'configID':configID, 'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    if toFile:
        call(f'mkdir -p {configs_path}contacts/', shell=True)
        dfconfigs.to_csv(f'{configs_path}contacts/{filename[:-4]}_loops_{loops}_ir_{interac_r}_contacts.csv', index=False)
    return dfconfigs, Nbots

    
def getContactsFromTrajParallel(filename, interac_r, loops, toFile=True):
    ticksPerCicle = loops*ticksPerLoop
    trajDF = pd.read_csv(configs_path+filename)
    # get a contact list from each configuration:
    ids = pd.unique(trajDF['ID'])
    Nbots = len(ids)
    Nconfigs = len(trajDF)/Nbots
    # is there any tick with more than 1 config?
    count = Counter(list(trajDF.loc[trajDF['ID']==0]['ticks']))
    ticks_plus1_configs = []
    for k,v in count.items():
        if v>1:
            ticks_plus1_configs.append(k)
    if(ticks_plus1_configs):
        print(f"There are {len(ticks_plus1_configs)} ticks with more than 1 config, from Nconfigs.")
    # search for contacts in each configuration and build the columns of a future dataframe:
    configID, cicleID, contacts0, contacts1 = [], [], [], []
    # keep in mind that if an initial time is discarded when generating the Traj, cicle=0 corresponds to a mid simulation time already
    dfconfigs = [trajDF.loc[(i*Nbots):(i*Nbots+Nbots-1)] for i in range(int(Nconfigs))]
    pool = mp.Pool(mp.cpu_count())
    res_async = tqdm([pool.apply_async(getContactsFromCicle, args = (df, i, ids, ticksPerCicle)) for i,df in enumerate(dfconfigs)])
    res = [r.get() for r in res_async]
    for confres in res:
        configID.extend(confres[0]), cicleID.extend(confres[1]), contacts0.extend(confres[2]), contacts1.extend(confres[3])
    pool.close()
    # build the dataframe:
    dfconfigs = pd.DataFrame({'configID':configID, 'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    dfconfigs.sort_values(by=['configID', 'contacts0'], inplace=True)
    if toFile:
        call(f'mkdir -p {configs_path}contacts/', shell=True)
        dfconfigs.to_csv(f'{configs_path}contacts/{filename[:-4]}_loops_{loops}_ir_{interac_r}_contacts.csv', index=False)
    return dfconfigs, Nbots
    
    
# EM PETA L'ORDINADOR...
def getContactsFromTrajOPT(filename, interac_r, loops, toFile=True):
    ticksPerCicle = loops*ticksPerLoop
    trajDF = pd.read_csv(configs_path+filename)
    # get a contact list from each configuration:
    ids = pd.unique(trajDF['ID'])
    Nbots = len(ids)
    Nconfigs = len(trajDF)/Nbots
    # is there any tick with more than 1 config?
    count = Counter(list(trajDF.loc[trajDF['ID']==0]['ticks']))
    ticks_plus1_configs = []
    for k,v in count.items():
        if v>1:
            ticks_plus1_configs.append(k)
    if(ticks_plus1_configs):
        print(f"There are {len(ticks_plus1_configs)} ticks with more than 1 config, from Nconfigs.")
    # search for contacts in each configuration and build the columns of a future dataframe:
    configID, cicleID, contacts0, contacts1 = [], [], [], []
    cicle = 0
    for i in tqdm(range(int(Nconfigs))):
        dfconfig = trajDF.loc[(i*Nbots):(i*Nbots+Nbots-1)]
        dfconfig.reset_index(drop=True, inplace=True)
        if int(dfconfig['ticks'][0]) > (cicle+1)*ticksPerCicle:
            cicle += 1
        positions = [(x,y) for (x,y) in zip(dfconfig['x_position'], dfconfig['y_position'])]
        contactCounter = 0
        for j,pos in enumerate(positions[:-1]):
            pos = positions[j]
            dists = [dist2D(pos1, pos) for pos1 in positions[j+1:]]
            contactsAgenti = [k+1+j for k,d in enumerate(dists) if d < 70.0]
            contacts0.extend([j]*len(contactsAgenti)), contacts1.extend(contactsAgenti)
            contactCounter += len(contacts0)
        configID.extend([i]*contactCounter)
        cicleID.extend([cicle]*contactCounter)
    # build the dataframe:
    dfconfigs = pd.DataFrame({'configID':configID, 'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    if toFile:
        call(f'mkdir -p {configs_path}contacts/', shell=True)
        dfconfigs.to_csv(f'{configs_path}contacts/{filename[:-4]}_loops_{loops}_ir_{interac_r}_contacts.csv', index=False)
    return dfconfigs, Nbots
    
# FER SERVIR AIXO? https://stackoverflow.com/questions/61840607/calculate-distance-between-various-points-of-a-dataframe-with-python-in-a-two-d
# segueix sent mes rapid l'original, pel que sembla
def getContactsFromTrajOPT2(filename, interac_r, loops, toFile=True):
    ticksPerCicle = loops*ticksPerLoop
    trajDF = pd.read_csv(configs_path+filename)
    # get a contact list from each configuration:
    ids = pd.unique(trajDF['ID'])
    Nbots = len(ids)
    Nconfigs = len(trajDF)/Nbots
    # is there any tick with more than 1 config?
    count = Counter(list(trajDF.loc[trajDF['ID']==0]['ticks']))
    ticks_plus1_configs = []
    for k,v in count.items():
        if v>1:
            ticks_plus1_configs.append(k)
    if(ticks_plus1_configs):
        print(f"There are {len(ticks_plus1_configs)} ticks with more than 1 config, from Nconfigs.")
    # search for contacts in each configuration and build the columns of a future dataframe:
    configID, cicleID, contacts0, contacts1 = [], [], [], []
    cicle = 0
    for i in tqdm(range(int(Nconfigs))):
        dfconfig = trajDF.loc[(i*Nbots):(i*Nbots+Nbots-1)]
        dfconfig.reset_index(drop=True, inplace=True)
        if int(dfconfig['ticks'][0]) > (cicle+1)*ticksPerCicle:
            cicle += 1
        for j,id0 in enumerate(ids[:-1]):
            contactsAgent0 = []
            pos0 = (dfconfig['x_position'][id0], dfconfig['y_position'][id0])
            distances = np.sqrt(((pos0[0] - dfconfig.x_position)**2 + (pos0[1] - dfconfig.y_position)**2))
            distances = distances[j+1:]
            contactsAgent0.extend([k+1+j for k,d in enumerate(distances) if d < interac_r])
            if contactsAgent0:
                configID.extend([i]*len(contactsAgent0)), cicleID.extend([cicle]*len(contactsAgent0))
                contacts0.extend([id0]*len(contactsAgent0)), contacts1.extend(contactsAgent0)
    # build the dataframe:
    dfconfigs = pd.DataFrame({'configID':configID, 'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    if toFile:
        call(f'mkdir -p {configs_path}contacts/', shell=True)
        dfconfigs.to_csv(f'{configs_path}contacts/{filename[:-4]}_loops_{loops}_ir_{interac_r}_contacts.csv', index=False)
    return dfconfigs, Nbots

    
def integrateContactList(filename, interac_r, loops, toFile=True):
    contactsDF = pd.read_csv(f'{configs_path}contacts/{filename}')
    contacts_path = configs_path + 'contacts/'
    cicles = pd.unique(contactsDF['cicleID'])
    cicleID, contacts0, contacts1 = [], [], []
    print('Integrating configurations in the same cycle')
    for cicle in tqdm(cicles):
        dfcicles = contactsDF.loc[contactsDF['cicleID']==cicle].copy(deep=True)
        dfcicles.drop(columns='configID', inplace=True)
        dfcicles.drop_duplicates(inplace=True)
        cicleID.extend([cicle] * len(dfcicles))
        contacts0.extend([i0 for i0 in dfcicles['contacts0']])
        contacts1.extend([i1 for i1 in dfcicles['contacts1']])
    # build dataframe:
    dfconfigsInt = pd.DataFrame({'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    if toFile:
        dfconfigsInt.to_csv(f'{contacts_path}{filename[:-4]}_cicleINT.csv', index=False)
    return dfconfigsInt
    
def main(maxFiles=False): # to get contacts from trajectory positions
    filenameRoot = f'PRW_nBots_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}' #001.csv'
    contactSufix = f'_loops_{loops}_ir_{interac_r}_contacts.csv'
    existingConfigs = len(glob.glob(f'{configs_path}/' + filenameRoot + '_*.csv'))
    existingContacts = len(glob.glob(configs_path + 'contacts/' + filenameRoot + '_*' + contactSufix))
    # if existingConfigs > 5:
    #     existingConfigs = 5
    if maxFiles:
        existingConfigs = maxFiles
    print(f'Generating contact files. \n Existing configurations: {existingConfigs}. \n Existing contact files: {existingContacts}')
    for i in range(existingConfigs):
        filename = filenameRoot + f'_{str(i+1).zfill(3)}.csv'
        contactFilename = filename[:-4] + contactSufix
        if not (os.path.exists(configs_path + 'contacts/' + contactFilename)):
            print(f'Generating contact file for configuration {str(i+1).zfill(3)}')
            # dfconfigs, Nbots = getContactsFromTrajParallel(filename, interac_r, loops)
            dfconfigs, Nbots = getContactsFromTraj(filename, interac_r, loops)
        
def main2(maxFiles=False): # to get integrated contacts from contact file from trajectory
    filenameRoot = f'PRW_nBots_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}'
    contactSufix = f'_loops_{loops}_ir_{interac_r}_contacts.csv'
    existingContactFiles = len(glob.glob(f'{configs_path}contacts/' + filenameRoot + '_*' + contactSufix))
    existingIntContactFiles = len(glob.glob(configs_path + 'contacts/' + filenameRoot + '_*' + contactSufix[:-4] + '_cicleINT.csv'))
    # if existingContactFiles > 5:
    #     existingContactFiles = 5
    if maxFiles:
        existingConfigs = maxFiles
    print(f'Generating contact files. \n Existing contact files: {existingContactFiles}. \n Existing integrated contact files: {existingIntContactFiles}')
    for i in range(existingContactFiles):
    # for i in range(5,10):
        filename = filenameRoot + f'_{str(i+1).zfill(3)}' + contactSufix
        intContactFilename = filename[:-4] + 'cicleINT.csv'
        print(intContactFilename)
        if not os.path.exists(configs_path + 'contacts/' + intContactFilename):
            dfconfigsInt = integrateContactList(filename, interac_r, loops)
    
if __name__ == '__main__':
    maxFiles = 3
    tstart = time()
    for ir in [40.0, 50.0, 60.0, 70.0, 80.0, 90.0]:
    # for ir in [70.0, ]:
        interac_r = ir
        main(maxFiles)
        main2(maxFiles)
    tend = time()
    print(f'time elapsed: {tend-tstart}')
    # getContactsFromTraj('PRW_nBots_35_ar_20.0_speed_7_speedVar_2_001.csv', 70.0, 800)
    # getContactsFromTraj('prova.csv', 70.0, 800)

