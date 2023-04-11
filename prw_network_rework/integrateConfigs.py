"""
this program generates the contact files from config files, and
integrated contact files from contact files
"""
import glob
import os
import numpy as np
import pandas as pd
import multiprocessing as mp
from tqdm import tqdm
from collections import Counter
from subprocess import call
from filesHandling_kilombo import *


# GLOBAL PARAMETERS:
timestep = 0.0103
ticksPerSecond = 31
ticksPerLoop = timestep*ticksPerSecond

def dist2D(pos0, pos1):
    return np.sqrt((pos0[0]-pos1[0])**2+(pos0[1]-pos1[1])**2)

##############################################################################################################################
##############################################################################################################################
################################################ FROM CONFIG TO CONTACT FILE #################################################
# all radius are in units CM!!!
def getContactsFromCicle(df: pd.DataFrame, confID: int, ids: "list[int]", interac_r: float, loops: int, ticksPerCicle: int):
    """
    interac_r r must be specified in cm
    """
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
            if(dist<interac_r*10):
               configID.append(confID), cicleID.append(cicle), contacts0.append(id0), contacts1.append(id1)
    return configID, cicleID, contacts0, contacts1

def getContactsFromTrajParallel(configNumber, N, arena_r, interac_r, loops, limitTrajConfigs = False, jumpTrajConfigs=False):
    global ticksPerLoop
    ticksPerCicle = loops*ticksPerLoop
    filename = getFilenameRoot(N, arena_r) + getFilenameNumber(configNumber) + getFilesExtension()
    filenameContact = getFilenameRoot(N, arena_r) + getFilenameNumber(configNumber) + getFilenameContactSufix(loops, interac_r)
    # if os.path.exists(f'{getConfigsPath()}/contacts/{filenameContact}'):
    #     return
    trajDF = pd.read_parquet(getConfigsPath()+ '/' + filename)
    # get a contact list from each configuration:
    ids = pd.unique(trajDF['ID'])
    Nbots = len(ids)
    Nconfigs = len(trajDF)/Nbots
    print(Nconfigs)
    # is there any tick with more than 1 config?
    count = Counter(list(trajDF.loc[trajDF['ID']==0]['ticks']))
    ticks_plus1_configs = []
    for k,v in count.items():
        if v>1:
            ticks_plus1_configs.append(k)
    if(ticks_plus1_configs):
        print(f"There are {len(ticks_plus1_configs)} ticks with more than 1 config, from Nconfigs.")
    # set a max number of configs per traj to speed things up...
    if limitTrajConfigs and limitTrajConfigs < Nconfigs:
        Nconfigs = limitTrajConfigs
    # keep in mind that if an initial time is discarded when generating the Traj, cicle=0 corresponds to a mid simulation time already
    dfconfigs = [trajDF.loc[(i*Nbots):(i*Nbots+Nbots-1)] for i in range(int(Nconfigs))]
    # otherwise, jump a certain number of trajectories to get more uncorrelated snapshots
    if jumpTrajConfigs:
        dfconfigs = dfconfigs[::jumpTrajConfigs]
    # search for contacts in each configuration and build the columns of a future dataframe:
    configID, cicleID, contacts0, contacts1 = [], [], [], []
    pool = mp.Pool(int(mp.cpu_count()/2)) # sembla que va mes rapid si /2 que el total o /1.5
    res_async = tqdm([pool.apply_async(getContactsFromCicle, args = (df, i, ids, interac_r, loops, ticksPerCicle)) for i,df in enumerate(dfconfigs)])
    res = [r.get() for r in res_async]
    for confres in res:
        configID.extend(confres[0]), cicleID.extend(confres[1]), contacts0.extend(confres[2]), contacts1.extend(confres[3])
    pool.close()
    # build the dataframe:
    dfconfigs = pd.DataFrame({'configID':configID, 'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    dfconfigs.sort_values(by=['configID', 'contacts0'], inplace=True)
    minCicle = min(dfconfigs['cicleID'])
    dfconfigs['cicleID'] = dfconfigs['cicleID'] - minCicle
    call(f'mkdir -p {getConfigsPath()}/contacts/', shell=True)
    # set datatypes:
    dfconfigs['configID'] = dfconfigs['configID'].astype('int16')
    dfconfigs['cicleID'] = dfconfigs['cicleID'].astype('int16')
    dfconfigs['contacts0'] = dfconfigs['contacts0'].astype('int16')
    dfconfigs['contacts1'] = dfconfigs['contacts1'].astype('int16')
    dfconfigs.to_parquet(f'{getConfigsPath()}/contacts/{filenameContact}', index=False)

def integrateContacts(configNumber, N, arena_r, interac_r, loops):
    filenameContact = getFilenameRoot(N, arena_r) + getFilenameNumber(configNumber) + getFilenameContactSufix(loops, interac_r)
    filenameContactInt = getFilenameRoot(N, arena_r) + getFilenameNumber(configNumber) + getFilenameContactIntSufix(loops, interac_r)
    if os.path.exists(filenameContactInt):
        return
    contactsDF = pd.read_parquet(getConfigsPath() + '/contacts/' + filenameContact)
    cicles = list(pd.unique(contactsDF['cicleID']))
    cicleID, contacts0, contacts1 = [], [], []
    print(f'Integrating configurations in the same cycle, loops = {loops}, interac_r = {interac_r}')
    # drop the last cycle as it may not be completed
    if loops > 0:
        cicles.pop()
    for cicle in tqdm(cicles): 
        dfcicles = contactsDF.loc[contactsDF['cicleID']==cicle].copy(deep=True)
        dfcicles = dfcicles.drop(columns='configID')
        dfcicles = dfcicles.drop_duplicates()
        cicleID.extend([cicle] * len(dfcicles))
        contacts0.extend([i0 for i0 in dfcicles['contacts0']])
        contacts1.extend([i1 for i1 in dfcicles['contacts1']])
    # build dataframe:
    dfconfigsInt = pd.DataFrame({'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    # set datatypes:
    dfconfigsInt['cicleID'] = dfconfigsInt['cicleID'].astype('int16')
    dfconfigsInt['contacts0'] = dfconfigsInt['contacts0'].astype('int16')
    dfconfigsInt['contacts1'] = dfconfigsInt['contacts1'].astype('int16')
    dfconfigsInt.to_parquet(getConfigsPath() + '/contacts/' + filenameContactInt)


# this is the main function to generate contact files for a given set of parameters
def configs_to_contacts(N, arena_r, interac_r, loops, maxFiles = False, jumpTrajConfigs=0):
    existingConfigs = len(glob.glob(getConfigsPath() + '/' + getFilenameRoot(N, arena_r) + '_*' + getFilesExtension()))
    existingContacts = len(glob.glob(getConfigsPath() + '/contacts/' + getFilenameRoot(N, arena_r) + '_*' + getFilenameContactSufix(loops, interac_r)))
    print(f'Generating contact files. \n Existing configurations: {existingConfigs}. \n Existing contact files: {existingContacts}')
    if maxFiles:
        existingConfigs = maxFiles
        print(f'Using {maxFiles} position files to generate contacts.')
    for i in range(1,existingConfigs+1):
        getContactsFromTrajParallel(i, N, arena_r, interac_r, loops, jumpTrajConfigs=jumpTrajConfigs)

# this is the main function to generate integrated contact files for a given set of parameters
def contacts_to_contactsInt(N, arena_r, interac_r, loops, maxFiles = False):
    existingContacts = len(glob.glob(getConfigsPath()+'/contacts/'+getFilenameRoot(N, arena_r)+'_*'+getFilenameContactSufix(loops, interac_r)))
    existingContactsInt = len(glob.glob(getConfigsPath()+'/contacts/'+getFilenameRoot(N, arena_r)+'_*'+getFilenameContactIntSufix(loops, interac_r)))
    if maxFiles and existingContacts > maxFiles:
        existingContacts = maxFiles
        print(f'Using {maxFiles} contact files to generate integrated contact files.')
    print(f'Generating integrated contact files. \n Existing contact files: {existingContacts}. \n Existing integrated contact files: {existingContactsInt}')
    for i in range(1,existingContacts+1):
        integrateContacts(i, N, arena_r, interac_r, loops)
        

# 7.0, 8.0, 9.0, 10.0
if __name__ == '__main__':
    mFiles = 4
    configs_to_contacts(492, 73.5, 3.6, 800, maxFiles=mFiles, jumpTrajConfigs=5)
    contacts_to_contactsInt(492, 73.5, 3.6, 800, maxFiles=mFiles)
    # for ir in [3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
    #     configs_to_contacts(492, 73.5, ir, 400, maxFiles=mFiles, jumpTrajConfigs=5)
    #     contacts_to_contactsInt(492, 73.5, ir, 400, maxFiles=mFiles)