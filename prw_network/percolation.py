import pandas as pd
import numpy as np
import igraph as ig
import subprocess
import os
import glob
import matplotlib.pyplot as plt

N = 492
arena_r = 75.0
speed = 9
speedVar = 2
contactsPath = 'raw_json_files/RWDIS_mod/configs/contacts/'
loops = 800

def getCommunitySizesSingleTraj(dfconfigsInt, N, excludeGiantComp=False, getGC = False):
    cicles = pd.unique(dfconfigsInt['cicleID'])
    components_sizes_allconf = []
    giantComp_allconf = []
    # discard first cycle, where bots may be out of the arena, and are slowly relocated
    cicleStart = 1
    for cicle in cicles[cicleStart:]:
        dfcicle = dfconfigsInt.loc[dfconfigsInt['cicleID']==cicle].copy(deep=True)
        dfcicle.drop(labels='cicleID', axis='columns', inplace=True)
        g = ig.Graph.DataFrame(dfcicle, directed=False)
        components = g.components()
        sum_check = 0
        components_sizes = []
        for i,com in enumerate(components):
            components_sizes.append(len(com))
            sum_check += len(com)
        if(sum_check != N):
            for _ in range(N-sum_check):
                components_sizes.append(1)
        if excludeGiantComp:
            index_max = max(range(len(components_sizes)), key=components_sizes.__getitem__)
            giantComp = components_sizes[index_max]
            components_sizes.remove(giantComp)
        if getGC:
            index_max = max(range(len(components_sizes)), key=components_sizes.__getitem__)
            giantComp = components_sizes[index_max]
            giantComp_allconf.append(giantComp)
        components_sizes_allconf.extend(components_sizes)
    if getGC:
        return components_sizes_allconf, giantComp_allconf
    else:
        return components_sizes_allconf
        
def getCommunitySizesAllTraj(N, interac_r, loops, excludeGiantComp=False, getGC=False):
    filenameRoot = f'PRW_nBots_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}'
    contactsIntSufix = f'_loops_{loops}_ir_{interac_r}_contacts_cicleINT.csv'
    existingFiles = len(glob.glob(contactsPath + filenameRoot + '_*' + contactsIntSufix))
    # print(existingFiles)
    com_sizes_all_configs = []
    giant_comp_all_configs = []
    for i in range(existingFiles):
        df = pd.read_csv(f'{contactsPath}' + filenameRoot + f'_{str(i+1).zfill(3)}' + contactsIntSufix)
        if getGC:
            com_sizes, giant_comps = getCommunitySizesSingleTraj(df, N, excludeGiantComp, getGC)
            giant_comp_all_configs.extend(giant_comps)
        else:
            com_sizes = getCommunitySizesSingleTraj(df, N, excludeGiantComp)
        com_sizes_all_configs.extend(com_sizes)
    if getGC:
        return com_sizes_all_configs, giant_comp_all_configs
    else:
        return com_sizes_all_configs
    
def meanClusterSize(com_sizes):
    com_sizes = np.array(com_sizes)
    sumSquared = np.sum(com_sizes**2)
    sumLin = np.sum(com_sizes)
    #print(sumSquared, sumLin)
    try:
        mcs = sumSquared/sumLin
    except RuntimeWarning:
        mcs = 0.0
    if len(com_sizes) == 0:
        mcs = 0
    return mcs
    
      
def getMeanClusterSize(N, arena_r, irs, loops):
    '''
    gets a dataframe with the irs and the corresponding MCS. Reads existing one, adds irs not in the df
    if irs < irs present in the df, right now you get all the irs in the df
    '''
    subprocess.call('mkdir -p other_res_files/', shell=True)
    filename = f'other_res_files/MeanClusterSize_N_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}_loops_{loops}.csv'
    if(os.path.exists(filename)):
        dfMCS = pd.read_csv(filename)
        irs_df = pd.unique(dfMCS['interac_r'])
        missing_irs = [ir for ir in irs if ir not in irs_df]
        # print(missing_irs, loops)
        if missing_irs:
            mcs_list = []
            for ir in missing_irs:
                com_sizes = getCommunitySizesAllTraj(N, ir, loops, excludeGiantComp=True)
                mcs = meanClusterSize(com_sizes)
                mcs_list.append(mcs)
            dfNewIrs = pd.DataFrame({'interac_r':missing_irs, 'mcs':mcs_list})
            dfMCS = pd.concat([dfMCS, dfNewIrs], ignore_index=True)
            dfMCS.sort_values(by='interac_r', inplace=True)
            dfMCS.to_csv(filename, index=False)
    else:
        mcs_list = []
        for ir in irs:
            com_sizes = getCommunitySizesAllTraj(N, ir, loops, excludeGiantComp=True)
            mcs = meanClusterSize(com_sizes)
            mcs_list.append(mcs)
        dfMCS = pd.DataFrame({'interac_r':irs, 'mcs':mcs_list})
        dfMCS.to_csv(filename, index=False)
    return dfMCS
    
def plotMeanClusterSize(N, arena_r, irs, loops):
    dfMCS = getMeanClusterSize(N, arena_r, irs, loops)
    fig, ax = plt.subplots()
    ax.set_xlabel('$r_i$')
    ax.set_ylabel('mean cluster size')
    fig.suptitle(f'N = {N}, $r_a = {arena_r}$, loops = {loops}')
    ax.plot(dfMCS['interac_r'], dfMCS['mcs'])
    fig.tight_layout()
    fig.savefig(f'MCS_N_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}_loops_{loops}.png')
    
def plotMeanClusterSize_loops(N, arena_r, irs_loops_dic, loops_list, quenched=False):
    fig, ax = plt.subplots()
    ax.set_xlabel('$r_i$')
    ax.set_ylabel('mean cluster size')
    fig.suptitle(f'N = {N}, $r_a = {arena_r}$')
    for loops in loops_list:
        irs = irs_loops_dic[loops]
        dfMCS = getMeanClusterSize(N, arena_r, irs, loops)
        ax.plot(dfMCS['interac_r'], dfMCS['mcs'], label=f'{loops}', marker='.', linewidth=0.8)
    if quenched:
        dfMCSq = pd.read_csv(f'quenched_results/MeanClusterSize_v0_nopush_N_{N}_ar_{arena_r}_er_1.5.csv')
        dfMCSq['interac_r'] *= 10
        ax.plot(dfMCSq['interac_r'], dfMCSq['mcs'], '.--k', label='Quenched (nopush)', linewidth=0.8)
    fig.legend(title='loops')
    fig.tight_layout()
    fig.savefig(f'MCS_N_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}_diffloops.png')


def getAvgGiantComponent(N, arena_r, irs, loops):
    subprocess.call('mkdir -p other_res_files/', shell=True)
    filename = f'other_res_files/AvgGiantComp_N_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}_loops_{loops}.csv'
    if(os.path.exists(filename)):
        dfAGC = pd.read_csv(filename)
        irs_df = pd.unique(dfAGC['interac_r'])
        missing_irs = [ir for ir in irs if ir not in irs_df]
        if missing_irs:
            avgGC_list, stdGC_list = [], []
            for ir in missing_irs:
                _, giant_comps = getCommunitySizesAllTraj(N, ir, loops, getGC = True)
                avgGC, stdGC = np.mean(giant_comps), np.std(giant_comps)
                avgGC_list.append(avgGC), stdGC_list.append(stdGC)
            dfNewIrs = pd.DataFrame({'interac_r':missing_irs, 'avgGC':avgGC_list, 'stdGC':stdGC_list})
            dfAGC = pd.concat([dfAGC, dfNewIrs], ignore_index=True)
            dfAGC.sort_values(by='interac_r', inplace=True)
            dfAGC.to_csv(filename, index=False)
    else:
        avgGC_list, stdGC_list = [], []
        for ir in irs:
            _, giant_comps = getCommunitySizesAllTraj(N, ir, loops, getGC =True)
            avgGC, stdGC = np.mean(giant_comps), np.std(giant_comps)
            avgGC_list.append(avgGC), stdGC_list.append(stdGC)
        dfAGC = pd.DataFrame({'interac_r':irs, 'avgGC':avgGC_list, 'stdGC':stdGC_list})
        dfAGC.to_csv(filename, index=False)
    return dfAGC

def plotAvgGiantComponent(N, arena_r, irs_loops_dic, loops_list, quenched=False):
    fig, ax = plt.subplots()
    ax.set_xlabel('$r_i$')
    ax.set_ylabel('Avg Giant Component')
    fig.suptitle(f'N = {N}, $r_a = {arena_r}$')
    for loops in loops_list:
        irs = irs_loops_dic[loops]
        dfAGC = getAvgGiantComponent(N, arena_r, irs, loops)
        # ax.plot(dfAGC['interac_r'], dfAGC['avgGC'], label=f'{loops}', marker='.')
        ax.errorbar(dfAGC['interac_r'], dfAGC['avgGC'], yerr=dfAGC['stdGC'], fmt='.-', linewidth=0.8, elinewidth=0.5, capsize=2.0, label=f'{loops}')
    if quenched:
        dfAGCquench = pd.read_csv('quenched_results/avgMaxCom_difN_dens_0.028_nopush.csv')
        dfAGCquench = dfAGCquench.loc[dfAGCquench['N']==N] #.copy(deep=True)
        # set interac_r to milimiters:
        dfAGCquench['interac_r'] *= 10
        ax.errorbar(dfAGCquench['interac_r'], dfAGCquench['avg'], dfAGCquench['std'], fmt='.--k', linewidth=0.8, elinewidth=0.5, capsize=2.0, label='Quench (nopush)')  
    ax.legend(title='loops', loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5))
    fig.tight_layout()
    fig.savefig(f'avgGC_N_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}_diffloops.png')



irs_loops_dic = {
    0: [40.0, 50.0, 60.0, 70.0, 80.0, 90.0],
    400: [40.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 100.0],
    # 800: [40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0],
    800: [40.0, 50.0, 60.0, 70.0, 80.0, 90.0],
    1200: [40.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0, 90.0]
}

def main():
    # plotMeanClusterSize(N, arena_r, irs, loops)
    loops = [800, ] #  [0, 400, 800, 1200]
    plotMeanClusterSize_loops(N, arena_r, irs_loops_dic, loops, quenched=False)
    # plotMeanClusterSize_loops(N, arena_r, irs, [0, 800])
    # to do: afegir aqui la comparacio amb configuracions aleatories del model quenched
    plotAvgGiantComponent(N, arena_r, irs_loops_dic, loops, quenched=False)

    
if __name__ == '__main__':
    main()

    
        
        

