import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import igraph as ig
import glob
from subprocess import call
import os
from math import pi

# EXPERIMENT: que passa si integros contactes de les configuracions quenched? MCS?
# de moment ho faig tot en aquest fitxer, si val la pena generalitzar ho moure a graph_prop_functions i percolation...
from graph_properties_functions import getConfigPath

# global var:
N = 492
exclusion_r = 1.5
arena_r = 75.0

def integrate_quenched(Nintegrate: int, N: int, exclusion_r: float, interac_r: float, arena_r: float, push: bool=False):
    configPath = getConfigPath(N, exclusion_r, arena_r, push)
    contactListCounter = len(glob.glob(f'{configPath}/contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'))
    if contactListCounter%2 != 0:
        contactListCounter -= 1
    if not os.path.exists(f'{configPath}/integrated_contacts/'):
        call(f'mkdir -p {configPath}/integrated_contacts/', shell=True)
        intContactListCounter = 0
    else:
        filenameWC = 'contact_list'
        for j in range(Nintegrate):
            filenameWC += '_*'
        filenameWC += f'_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.csv'
        intContactListCounter = len(glob.glob(f'{configPath}/integrated_contacts/{filenameWC}'))
    print(intContactListCounter)
    print(contactListCounter)
    for i in range(1+intContactListCounter*2,contactListCounter+1,2):
        dfs = []
        for j in range(Nintegrate):
            try:
                dfsingle = pd.read_csv(f'{configPath}/contact_list_{str(i+j).zfill(3)}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt', sep='\s+',header=None)
            except:
                continue
            dfs.append(dfsingle)
        df = pd.concat(dfs, ignore_index=True)
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.sort_values(by=[0,1], inplace=True)
        # write them:
        df[0] = df[0].astype('int16')
        df[1] = df[1].astype('int16')
        filename = 'contact_list'
        for j in range(Nintegrate):
            filename = filename + '_' + str(i+j).zfill(3)
        filename += f'_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.csv'
        df.to_csv(f'{configPath}/integrated_contacts/{filename}', index=False)


def getCommunitySizes_integrate_quenched(Nintegrate: int, N: int, exclusion_r: float, interac_r: float, arena_r: float, push: bool=False, excludeGiantComp: bool=False):
    configPath = getConfigPath(N, exclusion_r, arena_r, push) + '/integrated_contacts'
    filenameWC = 'contact_list' # WC = wild card
    for i in range(Nintegrate):
        filenameWC += '_*'
    filenameWC += f'_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.csv'
    contactLists = glob.glob(f'{configPath}/{filenameWC}')
    components_sizes = []
    for contList in contactLists:
        try:
            df = pd.read_csv(contList) # mind that header is "0 1" !!!
        except:
            continue
        if df.empty: continue
        g = ig.Graph.DataFrame(df, directed=False)
        components = g.components() # si hi ha un node sol, no el considera component (en realitat es com si no formes part del graph)
        sum_check = 0
        comps_prov = []
        for com in components:
            comps_prov.append(len(com))
            sum_check += len(com)
        if(sum_check != N):
            for _ in range(N-sum_check):
                comps_prov.append(1)
        if(excludeGiantComp):
            # detect giant component and exclude it from the list **es correcte, si la maxima component esta repetida (e.g. 10 10 8 7), borrar les dues? NO, borrar només una!!!
            index_max = max(range(len(comps_prov)), key=comps_prov.__getitem__)
            giantComp = comps_prov[index_max]
            comps_prov.remove(giantComp)
        components_sizes.extend(comps_prov)
    return components_sizes

def getMeanClusterSize_integrate_quenched(Nintegrate: int,  irs: list, exclusion_r: float, arena_r: float, N: int, push: bool):
    '''
    gets a dataframe with the irs and the corresponding MCS. Reads existing one, adds irs not in the df
    push: push/ nopush -> True/False
    if irs < irs present in the df, right now you get all the irs in the df
    '''
    call('mkdir -p other_res_files/', shell=True)
    pushID = 'push' if push else 'nopush'
    filename = f'other_res_files/MeanClusterSize_intQuench_Nint_{Nintegrate}_{pushID}_N_{N}_ar_{arena_r}_er_{exclusion_r}.csv'
    if(os.path.exists(filename)):
        dfMCS = pd.read_csv(filename)
        irs_df = pd.unique(dfMCS['interac_r'])
        missing_irs = [ir for ir in irs if ir not in irs_df]
        if missing_irs:
            mcs_list = []
            for ir in missing_irs:
                com_sizes = getCommunitySizes_integrate_quenched(Nintegrate, N, exclusion_r, ir, arena_r, push=push, excludeGiantComp=True)
                mcs = computeMeanClusterSize(com_sizes)
                mcs_list.append(mcs)
            dfNewIrs = pd.DataFrame({'interac_r':missing_irs, 'mcs':mcs_list})
            dfMCS = pd.concat([dfMCS, dfNewIrs], ignore_index=True)
            dfMCS.sort_values(by='interac_r', inplace=True)
            dfMCS['interac_r'] = dfMCS['interac_r'].astype('float32')
            dfMCS['mcs'] = dfMCS['mcs'].astype('float32')
            dfMCS.to_csv(filename, index=False)
    else:
        mcs_list = []
        for ir in irs:
            com_sizes = getCommunitySizes_integrate_quenched(Nintegrate, N, exclusion_r, ir, arena_r, push=push, excludeGiantComp=True)
            mcs = computeMeanClusterSize(com_sizes)
            mcs_list.append(mcs)
        dfMCS = pd.DataFrame({'interac_r':irs, 'mcs':mcs_list})
        dfMCS['interac_r'] = dfMCS['interac_r'].astype('float32')
        dfMCS['mcs'] = dfMCS['mcs'].astype('float32')
        dfMCS.to_csv(filename, index=False)
    return dfMCS

def computeMeanClusterSize(comsizes):
    comsizes = np.array(comsizes)
    a = np.sum(comsizes**2)
    b = np.sum(comsizes)
    try:
        mcs = a/b
    except RuntimeWarning:
        mcs = float('nan')
    if len(comsizes) == 0:
        mcs = float('nan')
    return mcs

def getAvgMaxComSize_integrate_quenched(Nintegrate: int, N: int, exclusion_r: float, interac_r: float , arena_r: float, push: bool=False):
    configPath = getConfigPath(N, exclusion_r, arena_r, push) + '/integrated_contacts'
    filenameWC = 'contact_list' # WC = wild card
    for i in range(Nintegrate):
        filenameWC += '_*'
    filenameWC += f'_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.csv'
    contactLists = glob.glob(f'{configPath}/{filenameWC}')
    max_com_sizes = []
    for contList in contactLists:
        df = pd.read_csv(contList)
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

def getAvgMaxComSize_different_system_size_integrate_quenched(Nintegrate: int, systems_info: dict, interac_r: float, exclusion_r: float, push: bool=False):
    '''
    systems_info is a dictionary with keys = population sizes, values = {'arena_r':XXX, ...}, e.g.
    systens_info = {35:{'arena_r':20.0, ...}, 219:{'arena_r':50.0, ...}}
    probably a simpler structure such as [(35, 20.0), (219, 50.0),...] could be used but for now it works with the idea used in "percolation.py"
    '''
    first_key = next(iter(systems_info))
    density = first_key/(pi*systems_info[first_key]['arena_r']**2)
    pushLabel = 'push' if push else 'nopush'
    Ns = list(systems_info.keys())
    filename = f'other_res_files/avgMaxCom_intQuench_Nint_{Nintegrate}_difN_dens_{round(density,3)}_{pushLabel}.csv'
    if(os.path.exists(filename)):
        df = pd.read_csv(filename)
        dfir = df.loc[df['interac_r']==interac_r]
        Ns_dfir = pd.unique(dfir['N'])
        missing_Ns = [N for N in Ns if N not in Ns_dfir]
        if missing_Ns:
            avgMCs, stdMCs = [], []
            for N in missing_Ns:
                arena_r = systems_info[N]['arena_r']
                avg, std = getAvgMaxComSize_integrate_quenched(Nintegrate, N, exclusion_r, interac_r, arena_r, push)
                avgMCs.append(avg), stdMCs.append(std)
            dfNewNs = pd.DataFrame({'N':missing_Ns, 'interac_r':[interac_r]*len(missing_Ns), 'avg':avgMCs, 'std':stdMCs})
            df = pd.concat([df, dfNewNs], ignore_index = True)
            df.sort_values(by=['interac_r', 'N'], inplace=True)
            df.to_csv(filename, index=False)
            dfir = df.loc[df['interac_r']==interac_r]
    else:
        avgMCs, stdMCs = [], []
        for N in Ns:
            arena_r = systems_info[N]['arena_r']
            avg, std = getAvgMaxComSize_integrate_quenched(Nintegrate, N, exclusion_r, interac_r, arena_r, push)
            avgMCs.append(avg), stdMCs.append(std)
        dfir = pd.DataFrame({'N':Ns, 'interac_r':[interac_r]*len(Ns), 'avg':avgMCs, 'std':stdMCs})
        dfir.to_csv(filename, index=False)
    return dfir


def main():
    # irs = [3.5, 3.8, 4.0, 4.2, 4.3, 4.4, 4.5, 5.0, 5.5, 6.0, 7.0]
    irs = [3.5, 3.8, 4.0, 4.2, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]
    for ir in irs:
        integrate_quenched(2, N, exclusion_r, ir, arena_r)
    getMeanClusterSize_integrate_quenched(2, irs, exclusion_r, arena_r, N, push=False)
    # systems_info = {35: {'arena_r': 20.0}}
    systems_info = {492: {'arena_r': 75.0}}
    for ir in irs:
        getAvgMaxComSize_different_system_size_integrate_quenched(2, systems_info, ir, exclusion_r )

if __name__ == '__main__':
    main()
    # integrate_quenched(2, N, exclusion_r, 3.8, arena_r)


