import pandas as pd
import json
import numpy as np
from collections import Counter
from tqdm import tqdm
import igraph as ig
import matplotlib.pyplot as plt
from os.path import isfile

arena_r = 20.0 # centimeters
exclusion_r = 1.5 # centimeters
interac_r = 70.0 # milimeters
# filename = '1'
filename = 'PRWCada3kiloticks'
loops = 800 # a cicle is made of 800 loops in the kilobot program
timestep = 0.0103 # seconds per loop
ticksPerSecond = 31
ticksPerLoop = timestep*ticksPerSecond
ticksPerCicle = loops*ticksPerLoop

def dist2D(pos0, pos1):
    return np.sqrt((pos0[0]-pos1[0])**2+(pos0[1]-pos1[1])**2)
    
def getContactsFromJson(filename, interac_r, ticksPerCicle, toFile=True):
    with open(f'{filename}.json', 'r') as f:
        data = json.loads(f.read())
    # Flatten data into a dataframe:
    # https://towardsdatascience.com/how-to-convert-json-into-a-pandas-dataframe-100b2ae1e0d8
    df = pd.json_normalize(data, record_path='bot_states', meta='ticks')
    # get a contact list from each configuration:
    ids = pd.unique(df['ID'])
    Nbots = len(ids)
    Nconfigs = len(df)/Nbots
    print(f'Reading json file with {Nconfigs} configurations of {Nbots} bots.')
    # is there any tick with more than 1 config?
    count = Counter(list(df.loc[df['ID']==0]['ticks']))
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
        dfconfig = df.loc[(i*Nbots):(i*Nbots+Nbots-1)]
        dfconfig.reset_index(drop=True, inplace=True)
        if int(dfconfig['ticks'][0]) > (cicle+1)*ticksPerCicle:
            #print(int(dfconfig['ticks'][0]), ticksPerCicle, i)
            #input('enter ')
            cicle += 1
        for j,id0 in enumerate(ids[:-1]):
            pos0 = (dfconfig['x_position'][id0], dfconfig['y_position'][id0])
            for id1 in ids[j+1:]:
                pos1 = (dfconfig['x_position'][id1], dfconfig['y_position'][id1])
                dist = dist2D(pos0, pos1)
                #print(f'Bot {id0} and bot {id1}, distance {dist}')
                #input('enter ')
                if(dist<interac_r):
                    configID.append(i), cicleID.append(cicle), contacts0.append(id0), contacts1.append(id1)
    # build the dataframe:
    dfconfigs = pd.DataFrame({'configID':configID, 'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    if toFile:
        dfconfigs.to_csv(f'{filename}_ir_{interac_r}.csv', index=False)
    return dfconfigs, Nbots


# INTEGRATE CONTACT LIST:
def integrateContactList(dfconfigs, interac_r, filename='None', toFile=False):
    cicles = pd.unique(dfconfigs['cicleID'])
    cicleID, contacts0, contacts1 = [], [], []
    print('Integrating configurations in the same cycle')
    for cicle in tqdm(cicles):
        dfcicles = dfconfigs.loc[dfconfigs['cicleID']==cicle]
        dfcicles.drop_duplicates()
        cicleID.extend([cicle] * len(dfcicles))
        contacts0.extend([i0 for i0 in dfcicles['contacts0']])
        contacts1.extend([i1 for i1 in dfcicles['contacts1']])
    # build dataframe:
    dfconfigsInt = pd.DataFrame({'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    if toFile:
        dfconfigsInt.to_csv(f'{filename}_ir_{interac_r}_cicleINT.csv', index=False)
    return dfconfigsInt
    
    
def getComponentSizesAndMaxComIDs(dfcicle, Nbots, excludeGiantComp=False): # aqui entraria df d'un cicle, amb columnes 'contacts0', 'contacts1'
    g = ig.Graph.DataFrame(dfcicle, directed=False)
    components = g.components()
    sum_check = 0
    components_sizes = []
    for i,com in enumerate(components):
        components_sizes.append(len(com))
        sum_check += len(com)
    if(sum_check != Nbots):
        for _ in range(Nbots-sum_check):
            components_sizes.append(1)
    index_max = max(range(len(components_sizes)), key=components_sizes.__getitem__)
    if excludeGiantComp:
        # max loc 
        giantComp = components_sizes[index_max]
        while giantComp in components_sizes:
            components_sizes.remove(giantComp)
    maxComIDs = components[index_max]
    return components_sizes, maxComIDs


def componentsInTime(dfconfigsInt, Nbots): # aqui entraria dfconfigs integrat, amb columnes 'cicleID', 'contacts0', 'contacts1'
    cicles = pd.unique(dfconfigsInt['cicleID'])
    components_in_time = []
    max_com_in_time = []
    max_com_IDs_in_time = []
    for cicle in cicles:
        dfcicle = dfconfigsInt.loc[dfconfigsInt['cicleID']==cicle].copy(deep=True)
        dfcicle.drop(labels='cicleID', axis='columns', inplace=True)
        comSizes, maxComIDs = getComponentSizesAndMaxComIDs(dfcicle, Nbots)
        # components_in_time.append(comSizes)
        components_in_time.extend(comSizes)
        max_com_in_time.append(max(comSizes))
        max_com_IDs_in_time.append(maxComIDs)
    return components_in_time, max_com_in_time, max_com_IDs_in_time
