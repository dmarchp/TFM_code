import pandas as pd
import numpy as np
import glob
import os
import subprocess
import igraph as ig
from math import pi

arena_r = 20.0

def getConfigPath(N, exclusion_r, arena_r=20.0, push=False):
    # if(exclusion_r > 0):
    #     configPath = f'../frozen_positions_new/positions_and_contacts/{N}_bots'
    # else:
    #     configPath = f'../frozen_positions/positions_and_contacts/{N}_bots'
    if(push):
        push_folder = 'configs_w_push'
    else:
        push_folder = 'configs_wo_push'
    #configPath = f'../frozen_positions_new/positions_and_contacts/{N}_bots/{push_folder}'
    configPath = f'/media/david/KINGSTON/quenched_configs/{N}_bots/{push_folder}'
    return configPath


def getBotRadialDistribution(N, exclusion_r, arena_r=20.0, x0=0, y0=0, r_ini=1, dr=1, push=False):
    configPath = getConfigPath(N, exclusion_r, arena_r, push)
    configCounter = len(glob.glob(f'{configPath}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'))
    #if(configCounter>100):
    #    configCounter = 100
    steps = int((arena_r-r_ini)/dr)+1
    allConfig_radial_count = np.array([0] * steps, dtype='f')
    allConfig_radial_count_sq = np.array([0] * steps, dtype='f')
    radii = []
    for i in range(steps):
        radii.append(r_ini+i*dr)
    radii = np.array(radii, dtype='f')
    for i in range(1, configCounter+1):
        posdf = pd.read_csv(f'{configPath}/bots_xy_positions_{str(i).zfill(3)}_ar_{arena_r}_er_{exclusion_r}.txt',
                            sep='\s+', header=None, index_col=False)
        posdf.rename(columns={0: 'bot_id', 1: 'x', 2: 'y'}, inplace=True)
        N_radial_count = []
        Nsq_radial_count = []
        counter = 0
        for r in radii:
            for index, row in posdf.iterrows():
                if(np.sqrt(row['x']**2+row['y']**2) < r):
                    counter += 1
                    posdf.drop(posdf.loc[posdf['bot_id'] == row['bot_id']].index, inplace=True)
            N_radial_count.append(counter)
            Nsq_radial_count.append(counter**2)
        N_radial_count = np.array(N_radial_count)
        Nsq_radial_count = np.array(Nsq_radial_count)
        allConfig_radial_count += N_radial_count
        allConfig_radial_count_sq += Nsq_radial_count
    allConfig_radial_count = allConfig_radial_count/float(configCounter)
    allConfig_radial_count_sq = allConfig_radial_count_sq/float(configCounter)
    allConfig_radial_count_var = allConfig_radial_count_sq - allConfig_radial_count**2
    return radii, allConfig_radial_count, allConfig_radial_count_var
    
def getCommunitySizes(N, exclusion_r, interac_r, arena_r=20.0, push=False, excludeGiantComp=False, exclusionVersion = 0):
    configPath = getConfigPath(N, exclusion_r, arena_r, push)
    configCounter = len(glob.glob(f'{configPath}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'))
    contactListCounter = len(glob.glob(f'{configPath}/contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'))
    if not contactListCounter == configCounter:
        wd = os.getcwd()
        os.chdir('../frozen_positions_new')
        subprocess.call(f'python generate_contact_list.py {N} {arena_r} {interac_r} {exclusion_r} {int(push)}', shell=True)
        os.chdir(wd)
        contactListCounter = len(glob.glob(f'{configPath}/contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'))        
    components_sizes = []
    for i in range(1,contactListCounter+1):
        try:
            df = pd.read_csv(f'{configPath}/contact_list_{str(i).zfill(3)}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt', sep='\s+',header=None)
        except:
            continue
        if df.empty: continue
        g = ig.Graph.DataFrame(df, directed=False)
        components = g.components() # si hi ha un node sol, no el considera component
        sum_check = 0
        comps_prov = []
        for com in components:
            #components_sizes.append(len(com))
            comps_prov.append(len(com))
            sum_check += len(com)
        if(sum_check != N):
            for _ in range(N-sum_check):
                #components_sizes.append(1)
                comps_prov.append(1)
        if(excludeGiantComp):
            if(exclusionVersion==0):
                # detect giant component and exclude it from the list **es correcte, si la maxima component esta repetida (e.g. 10 10 8 7), borrar les dues? NO, borrar només una!!!
                index_max = max(range(len(comps_prov)), key=comps_prov.__getitem__)
                giantComp = comps_prov[index_max]
                #while giantComp in comps_prov:
                #    comps_prov.remove(giantComp)
                comps_prov.remove(giantComp)
            elif(exclusionVersion==1):
                # version 1: we exclude the giant component only when it is of the size of the system
                while N in comps_prov:
                    comps_prov.remove(N)
        # mix everything in the same batch. This has an effect on how the mean cluster size is computed
        components_sizes.extend(comps_prov)
        # no mix
        # components_sizes.append(comps_prov)
    # ATENCIO: aquesta part s'haura de reprogramar si mantinc l'append en comptes de l'extend!!!    
    # once finsihed, exclude componens greater than the median (if exclusionVersion == 2):
    if excludeGiantComp and exclusionVersion == 2:
        median = np.median(components_sizes)
        components_sizes_reduced = []
        for c in components_sizes:
            if c < median:
                components_sizes_reduced.append(c)
        components_sizes = components_sizes_reduced
    return components_sizes
    
def getAvgMaxComSize(N, exclusion_r, interac_r, arena_r=20.0, push=False):
    configPath = getConfigPath(N, exclusion_r, arena_r, push)
    configCounter = len(glob.glob(f'{configPath}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'))
    contactListCounter = len(glob.glob(f'{configPath}/contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'))
    if not contactListCounter == configCounter:
        wd = os.getcwd()
        os.chdir('../frozen_positions_new')
        subprocess.call(f'python generate_contact_list.py {N} {arena_r} {interac_r} {exclusion_r} {int(push)}', shell=True)
        os.chdir(wd)
        contactListCounter = len(glob.glob(f'{configPath}/contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'))
    max_com_sizes = []
    for i in range(1,contactListCounter+1):
        df = pd.read_csv(f'{configPath}/contact_list_{str(i).zfill(3)}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt', sep='\s+',header=None)
        g = ig.Graph.DataFrame(df, directed=False)
        components = g.components() # si hi ha un node sol, no el considera component
        sum_check = 0
        comps_prov = []
        for com in components:
            comps_prov.append(len(com))
            sum_check += len(com)
        if(sum_check != N):
            for _ in range(N-sum_check):
                comps_prov.append(1)
        index_max = max(range(len(comps_prov)), key=comps_prov.__getitem__)
        giantComp = comps_prov[index_max]
        max_com_sizes.append(giantComp)
    avgMaxComSize = np.mean(max_com_sizes)
    stdMaxComSize = np.std(max_com_sizes)
    return avgMaxComSize, stdMaxComSize

def getBotDegrees(N, exclusion_r, interac_r, arena_r=20.0, push=False, missingContacts=False):
    configPath = getConfigPath(N, exclusion_r, arena_r, push)
    configCounter = len(glob.glob(f'{configPath}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'))
    contactListCounter = len(glob.glob(f'{configPath}/contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'))
    # print(configCounter, contactListCounter)
    if not contactListCounter == configCounter and missingContacts:
        wd = os.getcwd()
        os.chdir('../frozen_positions_new')
        subprocess.call(f'python generate_contact_list.py {N} {arena_r} {interac_r} {exclusion_r} {int(push)}', shell=True)
        os.chdir(wd)
        contactListCounter = configCounter
    degrees = []
    for i in range(1,contactListCounter+1):
        df = pd.read_csv(f'{configPath}/contact_list_{str(i).zfill(3)}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt', sep='\s+',header=None)
        g = ig.Graph.DataFrame(df, directed=False)
        graph_degrees = []
        for j in range(g.vcount()):
            graph_degrees.append(g.vs[j].degree())
        for j in range(g.vcount()-N):
            graph_degrees.append(0)
        degrees.extend(graph_degrees)
    return degrees
    
    
# mean cluster size si comsizes es una llista unica amb totes les configuracions barrejades    
def computeMeanClusterSize(comsizes, exclusion_r, interac_r, arena_r, N,  MCSversion=0, push=True):
    comsizes = np.array(comsizes)
    if MCSversion == 3:
        prePath = f'../frozen_positions_new/positions_and_contacts/{N}_bots'
        configPath = 'configs_w_push' if push else 'configs_wo_push'
        contactListCounter = len(glob.glob(f'{prePath}/{configPath}/contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'))
        b = contactListCounter*N
    elif MCSversion in [0, 1, 2]:
        b = np.sum(comsizes)
    a = np.sum(comsizes**2)
    if b==0:
        s = 0
    else:
        s = a/b
    return s
    
    
def getMeanClusterSize(irs, exclusion_r, arena_r, N, push, MCSversion=0):
    '''
    gets a dataframe with the irs and the corresponding MCS. Reads existing one, adds irs not in the df
    push: push/ nopush -> True/False
    version: as there are/will be diferent versions to compute the MCS a version parameter is added
    getCommunitySizes must be updated to have different versions of GiantCompExclusion. Right now only 0th version.
    if irs < irs present in the df, right now you get all the irs in the df
    '''
    subprocess.call('mkdir -p other_res_files/', shell=True)
    pushID = 'push' if push else 'nopush'
    if MCSversion in [0,1,2]:
        excVersion = MCSversion
    elif MCSversion == 3:
        excVersion = 0
    filename = f'other_res_files/MeanClusterSize_v{MCSversion}_{pushID}_N_{N}_ar_{arena_r}_er_{exclusion_r}.csv'
    if(os.path.exists(filename)):
        dfMCS = pd.read_csv(filename)
        irs_df = pd.unique(dfMCS['interac_r'])
        missing_irs = [ir for ir in irs if ir not in irs_df]
        if missing_irs:
            mcs_list = []
            for ir in missing_irs:
                com_sizes = getCommunitySizes(N, exclusion_r, ir, arena_r, push=push, excludeGiantComp=True, exclusionVersion=excVersion)
                mcs = computeMeanClusterSize(com_sizes, exclusion_r, ir, arena_r, N, MCSversion, push)
                mcs_list.append(mcs)
            dfNewIrs = pd.DataFrame({'interac_r':missing_irs, 'mcs':mcs_list})
            dfMCS = pd.concat([dfMCS, dfNewIrs], ignore_index=True)
            dfMCS.sort_values(by='interac_r', inplace=True)
            dfMCS.to_csv(filename, index=False)
    else:
        mcs_list = []
        for ir in irs:
            com_sizes = getCommunitySizes(N, exclusion_r, ir, arena_r, push=push, excludeGiantComp=True, exclusionVersion=excVersion)
            mcs = computeMeanClusterSize(com_sizes, exclusion_r, ir, arena_r, N, MCSversion, push)
            mcs_list.append(mcs)
        dfMCS = pd.DataFrame({'interac_r':irs, 'mcs':mcs_list})
        dfMCS.sort_values(by='interac_r', inplace=True) # in case that irs have been given unsorted
        dfMCS.to_csv(filename, index=False)
    return dfMCS
    
