import pandas as pd
import numpy as np
import igraph as ig
import subprocess
import os
import glob
import matplotlib.pyplot as plt

# N = 492
# arena_r = 75.0
speed = 9
N = 35
arena_r = 20.0
# speed = 7
speedVar = 2
contactsPath = 'raw_json_files/RWDIS_mod/configs/contacts/'
loops = 800

def getCommunitySizesSingleTraj(dfconfigsInt, N, excludeGiantComp=False, getGC = False):
    cicles = pd.unique(dfconfigsInt['cicleID'])
    components_sizes_allconf = []
    giantComp_allconf = []
    # discard first cycle, where bots may be out of the arena, and are slowly relocated
    cicleStart = 0
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

# should giant component be excluded?
def getDegreesSingleTraj(dfconfigs, N):
    cicles = pd.unique(dfconfigs['cicleID'])
    cicleStart = 0
    all_degrees = []
    for cicle in cicles[cicleStart:]:
        dfcicle = dfconfigs.loc[dfconfigs['cicleID']==cicle].copy(deep=True)
        dfcicle.drop(labels='cicleID', axis='columns', inplace=True)
        g = ig.Graph.DataFrame(dfcicle, directed=False)
        degrees = g.degree([g.vs[j] for j in range(g.vcount())])
        degrees.extend([0 for _ in range(N-g.vcount())])
        all_degrees.extend(degrees)
    return all_degrees
    

def getCommunitySizesAllTraj(N, interac_r, loops, excludeGiantComp=False, getGC=False):
    filenameRoot = f'PRW_nBots_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}'
    # contactsIntSufix = f'_loops_{loops}_ir_{interac_r}_contacts_cicleINT.csv'
    contactsIntSufix = f'_loops_{loops}_ir_{interac_r}_contacts_cicleINT.parquet'
    existingFiles = len(glob.glob(contactsPath + filenameRoot + '_*' + contactsIntSufix))
    # existingFiles = 1
    # print(existingFiles)
    com_sizes_all_configs = []
    giant_comp_all_configs = []
    for i in range(existingFiles):
        # df = pd.read_csv(f'{contactsPath}' + filenameRoot + f'_{str(i+1).zfill(3)}' + contactsIntSufix)
        df = pd.read_parquet(f'{contactsPath}' + filenameRoot + f'_{str(i+1).zfill(3)}' + contactsIntSufix)
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

def getDegreesAllTraj(N, interac_r, loops):
    filenameRoot = f'PRW_nBots_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}'
    contactsIntSufix = f'_loops_{loops}_ir_{interac_r}_contacts_cicleINT.parquet'
    existingFiles = len(glob.glob(contactsPath + filenameRoot + '_*' + contactsIntSufix))
    degrees_all_configs = []
    for i in range(existingFiles):
        df = pd.read_parquet(f'{contactsPath}{filenameRoot}_{str(i+1).zfill(3)}{contactsIntSufix}')
        degrees = getDegreesSingleTraj(df, N)
        degrees_all_configs.extend(degrees)
    return degrees_all_configs
    
def meanClusterSize(com_sizes):
    com_sizes = np.array(com_sizes)
    sumSquared = np.sum(com_sizes**2)
    sumLin = np.sum(com_sizes)
    #print(sumSquared, sumLin)
    try:
        mcs = sumSquared/sumLin
    except RuntimeWarning:
        mcs = float("nan")
    if len(com_sizes) == 0:
        mcs = float("nan")
    return mcs
    
      
def getMeanClusterSize(N, arena_r, irs, loops, computeMissingIrs = True):
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
        if missing_irs and computeMissingIrs:
            mcs_list = []
            for ir in missing_irs:
                # print(f'here for {loops} {ir}')
                com_sizes = getCommunitySizesAllTraj(N, ir, loops, excludeGiantComp=True)
                mcs = meanClusterSize(com_sizes)
                mcs_list.append(mcs)
            dfNewIrs = pd.DataFrame({'interac_r':missing_irs, 'mcs':mcs_list})
            dfMCS = pd.concat([dfMCS, dfNewIrs], ignore_index=True)
            dfMCS.sort_values(by='interac_r', inplace=True)
            dfMCS.to_csv(filename, index=False)
    else:
        irs_with_mcs, mcs_list = [], []
        for ir in irs:
            com_sizes = getCommunitySizesAllTraj(N, ir, loops, excludeGiantComp=True) # es podria paralelitzar
            if com_sizes:
                mcs = meanClusterSize(com_sizes)
                mcs_list.append(mcs)
                irs_with_mcs.append(ir)
        dfMCS = pd.DataFrame({'interac_r':irs_with_mcs, 'mcs':mcs_list})
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
    
def plotMeanClusterSize_loops(N, arena_r, irs_loops_dic, loops_list, quenched=False, missingIrs = True):
    fig, ax = plt.subplots()
    ax.set_xlabel('$r_i$')
    ax.set_ylabel('mean cluster size')
    fig.suptitle(f'N = {N}, $r_a = {arena_r}$')
    for loops in loops_list:
        irs = irs_loops_dic[loops]
        dfMCS = getMeanClusterSize(N, arena_r, irs, loops, computeMissingIrs = missingIrs)
        ax.plot(dfMCS['interac_r'], dfMCS['mcs'], label=f'{loops}', marker='.', linewidth=0.8)
    if quenched:
        dfMCSq = pd.read_csv(f'quenched_results/MeanClusterSize_v0_nopush_N_{N}_ar_{arena_r}_er_1.5.csv')
        dfMCSq['interac_r'] *= 10
        ax.plot(dfMCSq['interac_r'], dfMCSq['mcs'], '.--k', label='Quenched (nopush)', linewidth=0.8)
        if os.path.exists(f'quenched_results/MeanClusterSize_intQuench_Nint_2_nopush_N_{N}_ar_{arena_r}_er_1.5.csv'):
            dfMCSqi = pd.read_csv(f'quenched_results/MeanClusterSize_intQuench_Nint_2_nopush_N_{N}_ar_{arena_r}_er_1.5.csv')
            dfMCSqi['interac_r'] *= 10 
            ax.plot(dfMCSqi['interac_r'], dfMCSqi['mcs'], marker='.', ls='--', color='xkcd:gray', label='Int Quenched (nopush)', linewidth=0.8)
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
            print(ir)
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
        print(loops)
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
        if os.path.exists('quenched_results/avgMaxCom_intQuench_Nint_2_difN_dens_0.028_nopush.csv'):
            dfAGCqi = pd.read_csv('quenched_results/avgMaxCom_intQuench_Nint_2_difN_dens_0.028_nopush.csv')
            dfAGCqi = dfAGCqi.loc[dfAGCqi['N']==N]
            dfAGCqi['interac_r'] *= 10
            ax.errorbar(dfAGCqi['interac_r'], dfAGCqi['avg'], dfAGCqi['std'], lw=0.8, elinewidth=0.5, capsize=2.0, marker='.', ls='--', color='xkcd:gray', label='Int Quench (nopush)')
    ax.legend(title='loops', loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5))
    fig.tight_layout()
    fig.savefig(f'avgGC_N_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}_diffloops.png')


def componentsDistrBoxPlot(N, arena_r, irs, loops, infoLogFile=False):
    com_sizes_all_ir = []
    for ir in irs:
        com_sizes = getCommunitySizesAllTraj(N, ir, loops, excludeGiantComp=True)
        com_sizes_all_ir.append(com_sizes)
    fig, ax = plt.subplots()
    bp = ax.boxplot(com_sizes_all_ir, sym='+', labels=irs, showmeans=True)
    plt.setp(bp['fliers'], markersize=3.0)
    # ----- jitter datapoints -----
    xs = []
    for i in range(len(com_sizes_all_ir)):
        xs.append(np.random.normal(i + 1, 0.04, len(com_sizes_all_ir[i])))
    for x, val in zip(xs, com_sizes_all_ir):
        ax.scatter(x, val, alpha=0.1)
    fig.text(0.1, 0.97, f'N = {N}, $r_a$ = {arena_r}, loops = {loops}. Giant Component Excluded.')
    ax.set_xlabel('$r_i$')
    ax.set_ylabel('component sizes')
    fig.tight_layout()
    fig.savefig(f'com_sizes_boxplot_N_{N}_ra_{arena_r}_loops_{loops}_speed_{speed}_speedVar_{speedVar}.png')
    plt.close(fig)
    if infoLogFile:
        file = open(f'other_res_files/com_sizes_boxplot_N_{N}_ra_{arena_r}_loops_{loops}.log', 'w')
        file.write('interac_r, number of communities left after excluding giant component \n')
        for i,ir in enumerate(irs):
            file.write(f'{ir}, {len(com_sizes_all_ir[i])}, {com_sizes_all_ir[i][:20]}\n')
        file.close()

def componentsHistogram(N, arena_r, ir, loops):
    com_sizes = getCommunitySizesAllTraj(N, ir, loops, excludeGiantComp=True)
    fig, ax = plt.subplots()
    ax.hist(com_sizes, bins=N, range=(0,N))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(100,200)
    fig.text(0.1, 0.97, f'N = {N}, $r_a$ = {arena_r}, $r_i$ = {ir} loops = {loops}. GC excluded, total counts = {len(com_sizes)}')
    fig.tight_layout()
    fig.savefig(f'com_sizes_histogram_N_{N}_ra_{arena_r}_ri_{ir}_loops_{loops}_speed_{speed}_speedVar_{speedVar}_zoom.png')
    plt.close(fig)


def getAvgDegree(N, arena_r, irs, loops, computeMissingIrs = True):
    '''
    gets a dataframe with the irs and the corresponding average degree throughout the configurations. Reads existing one, adds irs not in the df
    If irs < irs present in the df, right now you get all the irs in the df
    '''
    subprocess.call('mkdir -p other_res_files/', shell=True)
    filename = f'other_res_files/AverageDegree_N_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}_loops_{loops}.csv'
    if(os.path.exists(filename)):
        dfAvgDegree = pd.read_csv(filename)
        irs_df = pd.unique(dfAvgDegree['interac_r'])
        missing_irs = [ir for ir in irs if ir not in irs_df]
        # print(missing_irs, loops)
        if missing_irs and computeMissingIrs:
            avgDegree_list, stdDegree_list = [], []
            for ir in missing_irs:
                degrees = getDegreesAllTraj(N, ir, loops)
                avgDegree_list.append(np.mean(degrees)), stdDegree_list.append(np.std(degrees))
            dfNewIrs = pd.DataFrame({'interac_r':missing_irs, 'avgDegree':avgDegree_list, 'stdDegree':stdDegree_list})
            dfAvgDegree = pd.concat([dfAvgDegree, dfNewIrs], ignore_index=True)
            dfAvgDegree.sort_values(by='interac_r', inplace=True)
            dfAvgDegree.to_csv(filename, index=False)
    else:
        avgDegree_list, stdDegree_list = [], []
        for ir in irs:
            degrees = getDegreesAllTraj(N, ir, loops)
            avgDegree_list.append(np.mean(degrees)), stdDegree_list.append(np.std(degrees))
        dfAvgDegree = pd.DataFrame({'interac_r':irs, 'avgDegree':avgDegree_list, 'stdDegree':stdDegree_list})
        dfAvgDegree.to_csv(filename, index=False)
    return dfAvgDegree

def plotAvgDegree(N, arena_r, irs_loops_dic, loops_list, quenched=False):
    fig, ax = plt.subplots()
    ax.set_xlabel('$r_i$')
    ax.set_ylabel('Avg Degree')
    fig.suptitle(f'N = {N}, $r_a = {arena_r}$')
    for loops in loops_list:
        irs = irs_loops_dic[loops]
        dfAD = getAvgDegree(N, arena_r, irs, loops)
        # ax.plot(dfAD['interac_r'], dfAD['avgGC'], label=f'{loops}', marker='.')
        ax.errorbar(dfAD['interac_r'], dfAD['avgDegree'], yerr=dfAD['stdDegree'], fmt='.-', linewidth=0.8, elinewidth=0.5, capsize=2.0, label=f'{loops}')
    if quenched:
        dfADquench = pd.read_csv(f'quenched_results/avgDegree_N_{N}_ar_{arena_r}_er_1.5_nopush.csv')
        # set interac_r to milimiters:
        dfADquench['interac_r'] *= 10
        ax.errorbar(dfADquench['interac_r'], dfADquench['avg'], dfADquench['std'], fmt='.--k', linewidth=0.8, elinewidth=0.5, capsize=2.0, label='Quench (nopush)')
    ax.legend(title='loops', loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5))
    fig.tight_layout()
    fig.savefig(f'avgDegree_N_{N}_ar_{arena_r}_speed_{speed}_speedVar_{speedVar}_diffloops.png')

# per les dades N=35, speed 9
irs_loops_dic = {
    0: [35.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0],
    400: [35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 90.0, 100.0, 110.0],
    800: [35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 90.0, 100.0, 110.0],
    1200: [40.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0, 90.0]
}

# per les dades N=492, speed 9
# irs_loops_dic = {
#     0: [35.0, 40.0, 50.0, 60.0, 70.0, 80.0, 85.0, 90.0, 95.0],
#     400: [35.0, 40.0, 45.0, 50.0, 60.0, 70.0, 80.0, 90.0],
#     800: [35.0, 40.0, 45.0, 50.0, 60.0, 70.0, 80.0, 90.0]
# }

# per les dades amb speed 7
# irs_loops_dic = {
#     0: [40.0, 50.0, 60.0, 70.0, 80.0, 90.0],
#     400: [40.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 100.0],
#     800: [40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 100.0],
#     1200: [40.0, 50.0, 60.0, 65.0, 70.0, 80.0, 90.0, 100.0]
# }

def main():
    # plotMeanClusterSize(N, arena_r, irs, loops)
    loops = [0, 400, 800] #  [0, 400, 800, 1200]
    #loops = []
    plotMeanClusterSize_loops(N, arena_r, irs_loops_dic, loops, quenched=True, missingIrs=True)
    # plotAvgGiantComponent(N, arena_r, irs_loops_dic, loops, quenched=True)
    # componentsDistrBoxPlot(N, arena_r, [float(i) for i in range(40,100,10)], 400, True)
    # ----------- average degree ----------
    # for k,v in irs_loops_dic.items():
    #     getAvgDegree(N, arena_r, v, k, True)
    # plotAvgDegree(N, arena_r, irs_loops_dic, [0,400,800], quenched=True)

    # componentsHistogram(N, arena_r, 60.0, 0)

    
if __name__ == '__main__':
    main()

