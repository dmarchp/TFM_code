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
json_path = 'raw_json_files/'
filename = 'PRWCada3kiloticks2'
contacts_path = 'contact_files/'
loops = 800 # a cicle is made of 800 loops in the kilobot program
timestep = 0.0103 # seconds per loop
ticksPerSecond = 31
ticksPerLoop = timestep*ticksPerSecond
# ticksPerCicle = loops*ticksPerLoop

def dist2D(pos0, pos1):
    return np.sqrt((pos0[0]-pos1[0])**2+(pos0[1]-pos1[1])**2)

def loadContactsFile(interac_r, loops):
    # interac_r in mm
    # read/get the configurations
    if isfile(f'{contacts_path}{filename}_loops_{loops}_ir_{interac_r}.csv'):
        dfconfigs = pd.read_csv(f'{contacts_path}{filename}_loops_{loops}_ir_{interac_r}.csv')
        maxID0 = max(pd.unique(dfconfigs['contacts0']))
        maxID1 = max(pd.unique(dfconfigs['contacts1']))
        maxID = max([maxID0, maxID1])
        Nbots = maxID+1
        print(f'Configuration dataframe for {filename} with loops = {loops} and r_i = {interac_r} already exists. The configurations contain {Nbots} bots.')
    else:
        print(f'Generating Contact file for {filename} with with loops = {loops} and r_i = {interac_r}')
        dfconfigs, Nbots = getContactsFromJson(filename, interac_r, loops)
    return dfconfigs, Nbots

def loadIntegreatedContactsFile(dfconfigs, interac_r, loops):
    # interac_r in mm
    # read/get the integrated file:
    if isfile(f'{contacts_path}{filename}_loops_{loops}_ir_{interac_r}_cicleINT.csv'):
        print(f'The Integrated Contact file for {filename} with loops = {loops} and r_i = {interac_r} already exists')
        dfConfigsInt = pd.read_csv(f'{contacts_path}{filename}_loops_{loops}_ir_{interac_r}_cicleINT.csv')
    else:
        print(f'Generating Integrated Contact file for {filename} with with loops = {loops} and r_i = {interac_r}')
        dfConfigsInt = integrateContactList(dfconfigs, interac_r, loops, filename, toFile=True)
    return dfConfigsInt

def discardInitialTime(dfconfigs, ciclesTD):
    dfconfigs = dfconfigs.loc[dfconfigs['cicleID']>ciclesTD].copy(deep=True)
    return dfconfigs

def getContactsFromJson(filename, interac_r, loops, toFile=True):
    ticksPerCicle = loops*ticksPerLoop
    with open(f'{json_path}{filename}.json', 'r') as f:
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
        dfconfigs.to_csv(f'{contacts_path}{filename}_loops_{loops}_ir_{interac_r}.csv', index=False)
    return dfconfigs, Nbots

# INTEGRATE CONTACT LIST:
def integrateContactList(dfconfigs, interac_r, loops, filename='None', toFile=False):
    cicles = pd.unique(dfconfigs['cicleID'])
    cicleID, contacts0, contacts1 = [], [], []
    print('Integrating configurations in the same cycle')
    for cicle in tqdm(cicles):
        dfcicles = dfconfigs.loc[dfconfigs['cicleID']==cicle].copy(deep=True)
        dfcicles.drop(columns='configID', inplace=True)
        dfcicles.drop_duplicates(inplace=True)
        cicleID.extend([cicle] * len(dfcicles))
        contacts0.extend([i0 for i0 in dfcicles['contacts0']])
        contacts1.extend([i1 for i1 in dfcicles['contacts1']])
    # build dataframe:
    dfconfigsInt = pd.DataFrame({'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    if toFile:
        dfconfigsInt.to_csv(f'{contacts_path}{filename}_loops_{loops}_ir_{interac_r}_cicleINT.csv', index=False)
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

# es veu LLEIG
def plotComponentsInTime(irs, filename):
    fig, ax = plt.subplots()
    for ir in irs:
        dfconfigs, Nbots = loadContactsFile(ir)
        dfconfigsInt = loadIntegreatedContactsFile(dfconfigs, ir)
        comsInTime, maxComsInTime, maxComIDsInTime = componentsInTime(dfconfigsInt, Nbots)
        ax.plot([i for i in range(len(maxComsInTime))], maxComsInTime, label=f'{ir}')
    ax.set_xlabel('cicle')
    ax.set_ylabel('Max Com Size')
    ax.set_yscale('log')
    ax.legend(title=r'$r_i$')
    fig.tight_layout()
    fig.savefig(f'{filename}_maxComInTime_dif_ir.png')

def plotMaxComponentsInTime_compareQuench(ir, filename):
    fig, ax = plt.subplots()
    dfconfigs, Nbots = loadContactsFile(ir)
    dfconfigsInt = loadIntegreatedContactsFile(dfconfigs, ir)
    comsInTime, maxComsInTime, maxComIDsInTime = componentsInTime(dfconfigsInt, Nbots)
    ax.plot([i for i in range(len(maxComsInTime))], maxComsInTime, label='kilombo', alpha=0.8)
    ax.axhline(np.mean(maxComsInTime), label='Average MaxC Kilombo', ls=':', color='xkcd:royal blue')
    # ax.axhline(np.mean(comsInTime), label='Average Kilombo', ls=':', color='xkcd:aqua')
    # get quenched averaged max component size:
    df = pd.read_csv('../sim_some_params_frozen/avgMaxComponents.csv')
    df = df.loc[(df['N']==Nbots) & (df['arena_r']==arena_r) & (df['interac_r']==round(ir/10,1)) & (df['exclusion_r']==1.5)]
    ax.axhline(float(df.loc[df['configType']=='push']['avgMaxCom']), label='Quenched Push', ls='--', color='xkcd:gray')
    ax.axhline(float(df.loc[df['configType']=='nopush']['avgMaxCom']), label='Quenched No Push', ls='-.', color='xkcd:tan')
    ax.legend()
    fig.text(0.1,0.97, rf'$r_a = {arena_r}, \; r_i = {ir/10}, \; r_e = {exclusion_r}, \; N = {Nbots}$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'{filename}_maxComInTime_ir_{ir/10}.png')
    plt.close(fig)


def meanClusterSize(dfconfigsInt, Nbots):
    cicles = pd.unique(dfconfigsInt['cicleID'])
    sumSquared = 0
    sumLin = 0
    for cicle in cicles:
        dfcicle = dfconfigsInt.loc[dfconfigsInt['cicleID']==cicle].copy(deep=True)
        dfcicle.drop(labels='cicleID', axis='columns', inplace=True)
        comSizes, maxComIDs = getComponentSizesAndMaxComIDs(dfcicle, Nbots, excludeGiantComp=True)
        sumSquared += sum([size**2 for size in comSizes])
        sumLin += sum(comSizes)
    # print(sumSquared, sumLin)
    if sumLin == 0:
        mcs = 0
    else:
        mcs = sumSquared/sumLin
    return mcs


def plotMeanClusterSize(irs, filename):
    # uses loops defined as global variable
    fig, ax = plt.subplots()
    mcs_irs = []
    irs_cm = [ir/10 for ir in irs]
    for ir in irs:
        dfconfigs, Nbots = loadContactsFile(ir, loops)
        dfconfigsInt = loadIntegreatedContactsFile(dfconfigs, ir, loops)
        dfconfigsInt = discardInitialTime(dfconfigsInt, ciclesTD=10)
        mcs = meanClusterSize(dfconfigsInt, Nbots)
        mcs_irs.append(mcs)
    # print(mcs_irs)
    ax.plot(irs_cm, mcs_irs)
    ax.set_xlabel(r'$r_i$ (cm)')
    ax.set_ylabel('Mean Cluster Size')
    fig.tight_layout()
    fig.savefig(f'{filename}_loops_{loops}_meanClusterSize.png')


def plotMeanClusterSize_difLoops(loopsList, irs, filename):
    fig, ax = plt.subplots()
    irs_cm = [ir/10 for ir in irs]
    for loops in loopsList:
        mcs_irs = []
        for ir in irs:
            dfconfigs, Nbots = loadContactsFile(ir, loops)
            dfconfigsInt = loadIntegreatedContactsFile(dfconfigs, ir, loops)
            dfconfigsInt = discardInitialTime(dfconfigsInt, ciclesTD=10)
            mcs = meanClusterSize(dfconfigsInt, Nbots)
            mcs_irs.append(mcs)
        ax.plot(irs_cm, mcs_irs, label=loops)
    ax.set_xlabel(r'$r_i$ (cm)')
    ax.set_ylabel('Mean Cluster Size')
    fig.legend(title='loops', loc=(0.1,0.8))
    fig.tight_layout()
    fig.savefig(f'{filename}_meanClusterSize_dif_loops.png')




        
def analyzeGraphs(dfconfigsInt, Nbots, filename): # aqui entraria dfconfigs integrat, amb columnes 'cicleID', 'contacts0', 'contacts1'
    cicles = pd.unique(dfconfigsInt['cicleID'])
    components_in_time = []
    max_com_IDs_in_time = []
    for cicle in cicles:
        dfcicle = dfconfigsInt.loc[dfconfigsInt['cicleID']==cicle].copy(deep=True)
        dfcicle.drop(labels='cicleID', axis='columns', inplace=True)
        g = ig.Graph.DataFrame(dfcicle, directed=False)
        components = g.components() # si hi ha un node sol, no el considera component
        sum_check = 0
        components_sizes = []
        for i,com in enumerate(components):
            components_sizes.append(len(com))
            sum_check += len(com)
        if(sum_check != Nbots):
            for _ in range(Nbots-sum_check):
                components_sizes.append(1)
        components_in_time.append(components_sizes)
        # max loc 
        index_max = max(range(len(components_sizes)), key=components_sizes.__getitem__)
        #input('enter ')
        #max_com_IDs = list(components[index_max]).sort()
        #max_com_IDs_in_time.append(max_com_IDs)
        max_com_IDs_in_time.append(components[index_max])
    # components sizes in time:
    max_com, second_com = [], []
    for components in components_in_time:
        components.sort(reverse=True)
        max_com.append(components[0])
        if len(components)>1:
            second_com.append(components[1])
        else:
            second_com.append(0)
    fig, ax = plt.subplots()
    ax.plot(cicles, max_com, label='Max Com')
    ax.plot(cicles, second_com, label='Sec Com')
    ax.set_xlabel('cicle')
    ax.set_ylabel('Component Size')
    fig.tight_layout()
    fig.savefig(f'{filename}_components_sizes_over_cicles.png')
    plt.close(fig)
    # identification of max compoent in time
    counter = 1
    max_com_duration = []
    cicles_count = []
    for i,com in enumerate(max_com_IDs_in_time[1:]):
        if(com == max_com_IDs_in_time[i-1]):
            counter += 1
        else:
            max_com_duration.append(counter)
            counter = 1
        cicles_count.append(counter)
    fig, ax = plt.subplots()
    ax.plot(cicles[1:], cicles_count)
    ax.set_xlabel('cicles')
    ax.set_ylabel('cicles duration of max com')
    fig.tight_layout()
    fig.savefig(f'{filename}_cicles_of_max_com.png')
    plt.close(fig)


# main:
def main_simple():
    # read/get the configurations
    if isfile(f'{filename}_ir_{interac_r}.csv'):
        print('Configuration dataframe already exists.')
        dfconfigs = pd.read_csv(f'{filename}_ir_{interac_r}.csv')
        maxID0 = max(pd.unique(dfconfigs['contacts0']))
        maxID1 = max(pd.unique(dfconfigs['contacts1']))
        maxID = max([maxID0, maxID1])
        Nbots = maxID+1
        print(f'The configurations contain {Nbots} bots.')
    else:
        dfconfigs, Nbots = getContactsFromJson(filename, interac_r, loops)
    # read/get the integrated file:
    if isfile(f'{filename}_ir_{interac_r}_cicleINT.csv'):
        print('The integrated file already exists')
        dfConfigsInt = pd.read_csv(f'{filename}_ir_{interac_r}_cicleINT.csv')
    else:
        dfconfigsInt = integrateContactList(dfconfigs, filename, toFile=True)
    # fes coses:
    analyzeGraphs(dfconfigsInt, Nbots, filename)

def main_full():
    interac_r_list = [40.0, 50.0, 60.0, 70.0, 80.0, 85.0, 90.0, 95.0, 100.0, 105.0, 110.0, 115.0, 120.0]
    loops_list = [400, 800]
    #plotComponentsInTime(interac_r_list, filename)
    #plotMaxComponentsInTime_compareQuench(40.0, filename)
    #plotMaxComponentsInTime_compareQuench(50.0, filename)
    #plotMaxComponentsInTime_compareQuench(60.0, filename)
    #plotMaxComponentsInTime_compareQuench(70.0, filename)
    #plotMaxComponentsInTime_compareQuench(80.0, filename)
    plotMeanClusterSize(interac_r_list, filename)
    # plotMeanClusterSize_difLoops(loops_list, interac_r_list, filename)
    # dfconfig, Nbots = loadContactsFile(40.0)
    # dfconfigINT = loadIntegreatedContactsFile(dfconfig, 40.0)

if __name__ == '__main__':
    main_full()
