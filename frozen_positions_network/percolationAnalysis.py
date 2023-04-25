"""
This program includes analysis functions to study percolation in quenched configs:
degree distribution, community sizes distibution, mean cluster size...
uses the N_bots/raw_data/ files...
"""
import glob
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys
from subprocess import call
from scipy.optimize import curve_fit
sys.path.append('../')
from package_global_functions import *
from filesHandling_quenched import *

# MEAN CLUSTER SIZE
def computeMeanClusterSize(N, arena_r, interac_r, exclusion_r, push, maxConfigs):
    """
    computes the mean cluster size for specific conditions: N, ar, ir, er...
    """
    pushLabel = 'push' if push else 'nopush'
    path = getConfigsPath(N)
    rawDataFilename = path + f'/raw_data/comSizesWoGc_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet'
    df = pd.read_parquet(rawDataFilename)
    configs = list(pd.unique(df['configID']))
    if maxConfigs and max(configs) > maxConfigs:
        # from 1 to maxConfig:
        configsToUse = configs[:maxConfigs+1]
        # or randomly select maxConfigs:
        # configsToUse = sample(configsToUse, k=maxConfigs)
        # configsToUse.sort()
    else:
        configsToUse = configs
    dfaux = df.query('configID in @configsToUse').copy()
    dfaux['comSizes_sq'] = dfaux['comSizes']**2
    a = sum(dfaux['comSizes'])
    b = sum(dfaux['comSizes_sq'])
    try:
        mcs = b/a
    except ZeroDivisionError:
        mcs = float('nan')
    return mcs
    
def getMeanClusterSize_ir(N, arena_r, exclusion_r, irs, push=False, maxConfigs=False):
    """
    gets the MCS along a set of interaction radius, for fixed N, ar, er, push
    maxConfigs == False, then use all available
    """
    pushLabel = 'push' if push else 'nopush'
    path = getConfigsPath(N)
    pDataPath, rDataPath = path + '/processed_data', path + '/raw_data'
    # if not maxConfigs:
    #     df = pd.read_parquet(rDataPath + f'/comSizesWoGc_N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet')
    #     configLabel = max(list(pd.unique(df['configID'])))
    # else:
    #     configLabel = maxConfigs
    if not os.path.exists(pDataPath):
        call(f'mkdir -p {pDataPath}', shell=True)
    filename = pDataPath + f'/meanClusterSize_{pushLabel}_N_{N}_ar_{arena_r}_er_{exclusion_r}.csv' # _{configLabel}_configs
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        missing_irs = [ir for ir in irs if ir not in list(df['interac_r'])]
        if missing_irs:
            mcs_l = []
            for ir in missing_irs:
                mcs = computeMeanClusterSize(N, arena_r, ir, exclusion_r, push, maxConfigs)
                mcs_l.append(mcs)
            df_missing_irs = pd.DataFrame({'interac_r':missing_irs, 'mcs':mcs_l})
            df = pd.concat([df, df_missing_irs], ignore_index=True)
            df = df.sort_values(by='interac_r')
            df.to_csv(filename, index=False)
    else:
        mcs_l = []
        for ir in irs:
            mcs = computeMeanClusterSize(N, arena_r, ir, exclusion_r, push, maxConfigs)
            mcs_l.append(mcs)
        df = pd.DataFrame({'interac_r':irs, 'mcs':mcs_l})
        df.to_csv(filename, index=False)
    return df


def plotMeanClusterSize_difN(arena_r, exclusion_r, Ns, push=False, maxConfigs=False):
    pushLabel = 'push' if push else 'nopush'
    fig, ax = plt.subplots()
    colors = plt.cm.gnuplot(np.linspace(0,1,len(Ns)))
    ax.set(xlabel=r'$r_{int}$', ylabel='MCS')
    for N,color in zip(Ns, colors):
        irs = availableIrs(N, arena_r, exclusion_r, push)
        dfmcs = getMeanClusterSize_ir(N, arena_r, exclusion_r, irs, push)
        ax.plot(dfmcs['interac_r'], dfmcs['mcs'], label=f'{N}', marker='.', lw=0.8, color=color)
    fig.legend(title='N')
    fig.tight_layout()
    fig.savefig(f'MCS_difN_ar_{arena_r}_er_{exclusion_r}_{pushLabel}.png')

def powerLaw(x,a,b):
    return a*x**b

def plotPercRadius_fromMCS_difN(arena_r, exclusion_r, Ns, push=False):
    perc_rs, perc_rs_err = [], [[], []]
    pushLabel = 'push' if push else 'nopush'
    for N in Ns:
        irs = availableIrs(N, arena_r, exclusion_r, push)
        dfmcs = getMeanClusterSize_ir(N, arena_r, exclusion_r, irs, push)
        maxMCS = max(dfmcs['mcs'])
        perc_r = float(dfmcs.query('mcs == @maxMCS')['interac_r'])
        perc_rs.append(perc_r)
        # find lower, upper errors:
        i = dfmcs[dfmcs.interac_r == perc_r].index[0]
        perc_r_l, perc_r_u = dfmcs.iloc[i-1].interac_r, dfmcs.iloc[i+1].interac_r
        perc_rs_err[0].append(perc_r-perc_r_l), perc_rs_err[1].append(perc_r_u - perc_r)
    fig, ax = plt.subplots()
    ax.set(xlabel='N', ylabel=r'$r_{int}^*$') # , xscale='log', yscale='log'
    # ax.plot(Ns, perc_rs, ls='-', lw=0.8, marker='.')
    ax.errorbar(Ns, perc_rs, perc_rs_err, lw=0.8, elinewidth=0.7, capsize=1.0)
    # fit:
    perc_rs_sigma = [(l+u)/2 for l,u in zip(perc_rs_err[0],perc_rs_err[1])]
    paramfit, covfit = curve_fit(powerLaw, Ns, perc_rs, sigma=perc_rs_sigma)
    fit = powerLaw(Ns, *paramfit)
    ax.plot(Ns, fit, ls='--', lw=0.8, color='k')
    ax.text(0.7, 0.6, rf'{round(paramfit[0],3)} N**({round(paramfit[1],3)})', fontsize=8, color='k', transform=ax.transAxes)
    ax.text(0.7, 0.55, rf'{round(paramfit[1],8)} +- {round(np.sqrt(covfit[1,1]),8)}', fontsize=8, color='k', transform=ax.transAxes)
    # theoretical value:
    # ax.plot(Ns, 3.9*36*np.array(Ns)**(-1/2), ls='-.', color='xkcd:red', lw=0.9)
    ax.plot(Ns, 36*np.array(Ns)**(-1/2), ls='-.', color='xkcd:red', lw=0.9)
    ax.text(0.7, 0.65, rf'Theoretical, $r_{{int}}^* \sim N^{{-1/2}}$', fontsize=8, color='xkcd:red', transform=ax.transAxes)
    print(perc_rs)
    fig.tight_layout()
    fig.savefig(f'percR_MCS_difN_ar_{arena_r}_er_{exclusion_r}_{pushLabel}.png')


# MCS en funció d'N mantentint el r_i fixe...
def getMeanClusterSize_N(interac_r, arena_r, exclusion_r, Ns, push=False):
    '''
    gets the MCS along N for a given interac_r
    '''
    pushLabel = 'push' if push else 'nopush'
    path = getExternalSSDpath() + '/quenched_configs/manyN_processed_data/'
    filename = path + f'meanClusterSize_{pushLabel}_ir_{interac_r}_ar_{arena_r}_er_{exclusion_r}.csv'
    if not os.path.exists(path):
        call(f'mkdir -p {path}', shell=True)
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        missing_Ns = [N for N in Ns if N not in list(df['N'])]
        if missing_Ns:
            mcs = []
            for N in missing_Ns:
                avIrs = availableIrs(N, arena_r, exclusion_r, push)
                if interac_r not in avIrs:
                    avIrs.append(interac_r)
                    avIrs = sorted(avIrs)
                dfmcs = getMeanClusterSize_ir(N, arena_r, exclusion_r, avIrs, push)
                mcs.append(float(dfmcs.query('interac_r == @interac_r')['mcs']))
            # concatenate dfs
            df_missing_Ns = pd.DataFrame({'N':missing_Ns, 'mcs':mcs})
            df = pd.concat([df, df_missing_Ns], ignore_index=True)
            df = df.sort_values(by='N')
            df.to_csv(filename, index=False)
    else:
        mcs = []
        for N in Ns:
            avIrs = availableIrs(N, arena_r, exclusion_r, push)
            if interac_r not in avIrs:
                avIrs.append(interac_r)
                avIrs = sorted(avIrs)
            dfmcs = getMeanClusterSize_ir(N, arena_r, exclusion_r, avIrs, push)
            mcs.append(float(dfmcs.query('interac_r == @interac_r')['mcs']))
        df = pd.DataFrame({'N':Ns, 'mcs':mcs})
        df.to_csv(filename, index=False)
    return df
    

def plotMeanClusterSize_funcN(arena_r, irs, exclusion_r, Ns, push=False):
    fig, ax = plt.subplots()
    colors = plt.cm.rainbow(np.linspace(0,1,len(irs)))
    ax.set(xlabel='N', ylabel='MCS')
    for ir, c in zip(irs, colors):
        df = getMeanClusterSize_N(ir, arena_r, exclusion_r, Ns, push)
        ax.plot(df['N'], df['mcs'], ls='-', color = c, lw=0.8, marker='.', label=f'{ir}')
    fig.legend(title=r'$r_{int}$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'provant_MCS_funcN_difIr.png')

def Nstar(ir, a):
    return a*ir**(-2)

def plotPercN_fromMCS_difir(arena_r, exclusion_r, irs, Ns, push=False):
    perc_Ns, perc_Ns_err = [], [[], []]
    for ir in irs:
        dfmcs = getMeanClusterSize_N(ir, arena_r, exclusion_r, Ns, push)
        maxMCS = max(dfmcs['mcs'])
        perc_N = int(dfmcs.query('mcs == @maxMCS')['N'])
        perc_Ns.append(perc_N)
        # find lower, upper errors:
        i = dfmcs[dfmcs.N == perc_N].index[0]
        perc_N_l, perc_N_u = dfmcs.iloc[i-1].N, dfmcs.iloc[i+1].N
        perc_Ns_err[0].append(perc_N-perc_N_l), perc_Ns_err[1].append(perc_N_u - perc_N)
    fig, ax = plt.subplots()
    ax.set(xlabel='$r_{int}$', ylabel=r'$N^*$', xscale='log', yscale='log') # , xscale='log', yscale='log'
    # ax.plot(irs, perc_Ns, ls='-', lw=0.8, color='r', marker='.')
    ax.errorbar(irs, perc_Ns, perc_Ns_err, lw=0.8, elinewidth=0.7, capsize=1.0)
    # fit:
    paramfit, covfit = curve_fit(powerLaw, irs, perc_Ns)
    fit = powerLaw(irs, *paramfit)
    ax.plot(irs, fit, ls='--', lw=0.8, color='k')
    ax.text(0.7, 0.6, rf'{round(paramfit[0],3)} $r_{{int}}$**({round(paramfit[1],3)})', fontsize=8, color='k', transform=ax.transAxes)
    # theoretical:
    # a, _ = curve_fit(Nstar, np.array(irs), perc_Ns)
    # print(a)
    # teofit = Nstar(np.array(irs), a)
    # ax.plot(irs, teofit, color='xkcd:red', ls='-.', lw=0.9)
    ax.plot(irs, 1700*np.array(irs)**(-2), color='xkcd:red', ls='-.', lw=0.9)
    ax.text(0.7, 0.65, r'$N^* \sim r_{{int}}^{-2}$', fontsize=9, color='xkcd:red', transform=ax.transAxes)
    fig.tight_layout()
    fig.savefig('provant_percN_MCS_difir.png')









# Average giant component:

def computeAvgGiantComp(N, arena_r, interac_r, exclusion_r, push, maxConfigs):
    """
    computes the mean cluster size for specific conditions: N, ar, ir, er...
    """
    pushLabel = 'push' if push else 'nopush'
    path = getConfigsPath(N)
    rawDataFilename = path + f'/raw_data/comSizes_of_Gc_N_{N}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}_{pushLabel}.parquet'
    df = pd.read_parquet(rawDataFilename)
    configs = list(pd.unique(df['configID']))
    if max(configs) > maxConfigs:
        configsToUse = configs[:maxConfigs+1]
    else:
        configsToUse = configs
    df = df.query('configID in @configsToUse').copy()
    return df['comSizes'].mean(), df['comSizes'].std()


def getAvgGiantComp_ir(N, arena_r, exclusion_r, irs, push=False, maxConfigs=False):
    """
    gets the average giant component along a set of interaction radius, for fixed N, ar, er, push
    maxConfigs == False, then use all available
    """
    pushLabel = 'push' if push else 'nopush'
    path = getConfigsPath(N)
    pDataPath, rDataPath = path + '/processed_data', path + '/raw_data'
    if not os.path.exists(pDataPath):
        call(f'mkdir -p {pDataPath}', shell=True)
    filename = pDataPath + f'/avgGiantComp_{pushLabel}_N_{N}_ar_{arena_r}_er_{exclusion_r}.csv' # _{configLabel}_configs
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        missing_irs = [ir for ir in irs if ir not in list(df['interac_r'])]
        if missing_irs:
            avgs, stds = []
            for ir in missing_irs:
                avg, std = computeAvgGiantComp(N, arena_r, ir, exclusion_r, push, maxConfigs)
                avgs.append(avg), stds.append(std)
            df_missing_irs = pd.DataFrame({'interac_r':missing_irs, 'avg':avgs, 'std':stds})
            df = pd.concat([df, df_missing_irs], ignore_index=True)
            df = df.sort_values(by='interac_r')
            df.to_csv(filename, index=False)
    else:
        avgs, stds = [], []
        for ir in irs:
            avg, std = computeAvgGiantComp(N, arena_r, ir, exclusion_r, push, maxConfigs)
            avgs.append(avg), stds.append(std)
        df = pd.DataFrame({'interac_r':irs, 'avg':avgs, 'std':stds})
        df.to_csv(filename, index=False)
    return df

def main():
    # N, ar, er = 35, 20.0, 1.5
    N, ar, er = 492, 75.0, 1.5
    irs = availableIrs(N, ar, er, push=False)
    #print(irs)
    # per 492 que n'hagi generat les llistes de comsizes
    irs = [3.5, 4.0, 5.0, 5.5, 6.0, 6.3, 6.4, 6.5, 6.6, 6.7, 7.0, 7.5, 8.0, 9.0, 10.0]
    # getMeanClusterSize_ir(N, ar, er, irs, maxConfigs=1000) # maxConfigs 144 for N=492, 1000 for N=35
    getAvgGiantComp_ir(N, ar, er, irs, maxConfigs=1000)
    
if __name__ == '__main__':
    # plotMeanClusterSize_difN(20.0, 1.5, [10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80])
    plotPercRadius_fromMCS_difN(20.0, 1.5, [15, 20, 25, 30, 35, 40, 50, 60, 70, 80])
    # plotMeanClusterSize_funcN(20.0, [4.0, 5.0, 6.0, 7.0, 8.0, 9.0], 1.5, [10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80])
    # plotPercN_fromMCS_difir(20.0, 1.5, [5.0, 6.0, 7.0, 8.0, 9.0], [10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80])
    # plotMeanClusterSize_difN(75.0, 1.5, [352, 492, 633, 703, 844, 984])
    # plotPercRadius_fromMCS_difN(75.0, 1.5, [352, 492, 633, 703, 844, 984])
    



