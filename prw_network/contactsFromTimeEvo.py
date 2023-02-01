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
loops = 400

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
        # set datatypes:
        dfconfigs['configID'] = dfconfigs['configID'].astype('int16')
        dfconfigs['cicleID'] = dfconfigs['cicleID'].astype('int16')
        dfconfigs['contacts0'] = dfconfigs['contacts0'].astype('int16')
        dfconfigs['contacts1'] = dfconfigs['contacts1'].astype('int16')
        # write to file:
        dfconfigs.to_parquet(f'{configs_path}contacts/{filename[:-4]}_loops_{loops}_ir_{interac_r}_contacts.parquet', index=False)
        # dfconfigs.to_csv(f'{configs_path}contacts/{filename[:-4]}_loops_{loops}_ir_{interac_r}_contacts.csv', index=False)
    return dfconfigs, Nbots

    
def getContactsFromTrajParallel(filename, interac_r, loops, toFile=True):
    ticksPerCicle = loops*ticksPerLoop
    # trajDF = pd.read_csv(configs_path+filename)
    trajDF = pd.read_parquet(configs_path+filename)
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
        # set datatypes:
        dfconfigs['configID'] = dfconfigs['configID'].astype('int16')
        dfconfigs['cicleID'] = dfconfigs['cicleID'].astype('int16')
        dfconfigs['contacts0'] = dfconfigs['contacts0'].astype('int16')
        dfconfigs['contacts1'] = dfconfigs['contacts1'].astype('int16')
        # write to file:
        dfconfigs.to_parquet(f'{configs_path}contacts/{filename[:-8]}_loops_{loops}_ir_{interac_r}_contacts.parquet', index=False)
        # dfconfigs.to_csv(f'{configs_path}contacts/{filename[:-4]}_loops_{loops}_ir_{interac_r}_contacts.csv', index=False)
    return dfconfigs, Nbots

    
def integrateContactList(filename, interac_r, loops, toFile=True):
    # contactsDF = pd.read_csv(f'{configs_path}contacts/{filename}')
    contactsDF = pd.read_parquet(f'{configs_path}contacts/{filename}')
    contacts_path = configs_path + 'contacts/'
    cicles = pd.unique(contactsDF['cicleID'])
    cicleID, contacts0, contacts1 = [], [], []
    print(f'Integrating configurations in the same cycle, loops = {loops}, interac_r = {interac_r}')
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
        # set datatypes:
        dfconfigsInt['cicleID'] = dfconfigsInt['cicleID'].astype('int16')
        dfconfigsInt['contacts0'] = dfconfigsInt['contacts0'].astype('int16')
        dfconfigsInt['contacts1'] = dfconfigsInt['contacts1'].astype('int16')
        # write:
        # dfconfigsInt.to_csv(f'{contacts_path}{filename[:-4]}_cicleINT.csv', index=False)
        dfconfigsInt.to_parquet(f'{contacts_path}{filename[:-8]}_cicleINT.parquet', index=False)
    return dfconfigsInt


def main(maxFiles=False): # to get contacts from trajectory positions
    # csv files:
    # filenameRoot = f'PRW_nBots_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}' #001.csv'
    # contactSufix = f'_loops_{loops}_ir_{interac_r}_contacts.csv'
    # existingConfigs = len(glob.glob(f'{configs_path}/' + filenameRoot + '_*.csv'))
    # parquet files:
    filenameRoot = f'PRW_nBots_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}' #001.parquet'
    contactSufix = f'_loops_{loops}_ir_{interac_r}_contacts.parquet'
    existingConfigs = len(glob.glob(f'{configs_path}/' + filenameRoot + '_*.parquet'))    
    existingContacts = len(glob.glob(configs_path + 'contacts/' + filenameRoot + '_*' + contactSufix))
    # if existingConfigs > 5:
    #     existingConfigs = 5
    if maxFiles:
        existingConfigs = maxFiles
    print(f'Generating contact files. \n Existing configurations: {existingConfigs}. \n Existing contact files: {existingContacts}')
    for i in range(existingConfigs):
        # filename = filenameRoot + f'_{str(i+1).zfill(3)}.csv'
        # contactFilename = filename[:-4] + contactSufix
        filename = filenameRoot + f'_{str(i+1).zfill(3)}.parquet'
        contactFilename = filename[:-8] + contactSufix
        if not (os.path.exists(configs_path + 'contacts/' + contactFilename)):
            print(f'Generating contact file for configuration {str(i+1).zfill(3)}')
            dfconfigs, Nbots = getContactsFromTrajParallel(filename, interac_r, loops)
            # dfconfigs, Nbots = getContactsFromTraj(filename, interac_r, loops)


def main2(maxFiles=False): # to get integrated contacts from contact file from trajectory
    filenameRoot = f'PRW_nBots_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}'
    # contactSufix = f'_loops_{loops}_ir_{interac_r}_contacts.csv'
    contactSufix = f'_loops_{loops}_ir_{interac_r}_contacts.parquet'
    existingContactFiles = len(glob.glob(f'{configs_path}contacts/' + filenameRoot + '_*' + contactSufix))
    # existingIntContactFiles = len(glob.glob(configs_path + 'contacts/' + filenameRoot + '_*' + contactSufix[:-4] + '_cicleINT.csv'))
    existingIntContactFiles = len(glob.glob(configs_path + 'contacts/' + filenameRoot + '_*' + contactSufix[:-8] + '_cicleINT.parquet'))
    if maxFiles:
        existingContactFiles = maxFiles
    print(f'Generating integrated contact files. \n Existing contact files: {existingContactFiles}. \n Existing integrated contact files: {existingIntContactFiles}')
    for i in range(existingContactFiles):
        filename = filenameRoot + f'_{str(i+1).zfill(3)}' + contactSufix
        # intContactFilename = filename[:-4] + 'cicleINT.csv'
        intContactFilename = filename[:-8] + '_cicleINT.parquet'
        if not os.path.exists(configs_path + 'contacts/' + intContactFilename):
            dfconfigsInt = integrateContactList(filename, interac_r, loops)


if __name__ == '__main__':
    maxFiles = 10
    tstart = time()
    for ir in [35.0, 40.0, 45.0, 50.0, 60.0, 70.0, 80.0, 90.0]:
    # for ir in [70.0, ]:
        interac_r = ir
        main(maxFiles)
        main2(maxFiles)
    tend = time()
    print(f'time elapsed: {tend-tstart}')
    # getContactsFromTraj('PRW_nBots_35_ar_20.0_speed_7_speedVar_2_001.csv', 70.0, 800)
    # getContactsFromTraj('prova.csv', 70.0, 800)

