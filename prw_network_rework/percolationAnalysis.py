"""
This program includes analysis functions to study percolation in kilombo configs:
degree distribution, community sizes distibution, mean cluster size...
uses the raw_data/ files...
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from subprocess import call
from random import sample
import sys
sys.path.append('../')
from package_global_functions import *
from processConfigs import *
from filesHandling_kilombo import *

# Average Degree as a function of the interaction radius:
# def getAvgDegree():
#     ...

# Degree distribution:
def getDegreeDistrKilombo(N, arena_r, interac_r, loops, toFile = True):
    '''
    gets the Degree distribution for a specific interaction radius and integration time (loops)
    checks if it has already been computed and stored, if not computes it
    '''
    processedDataPath = getConfigsPath() + '/processed_data'
    distrFilename = f'degreeDistr_N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.csv'
    if os.path.exists(processedDataPath + '/' + distrFilename):
        df = pd.read_csv(processedDataPath + '/' + distrFilename)
    else:
        rawDataFilename = getConfigsPath() + '/raw_data/' + f'degrees_N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet'
        if not os.path.exists(rawDataFilename):
            getDegreesAllTraj(N, arena_r, interac_r, loops)
        dfdegrees = pd.read_parquet(rawDataFilename)
        binCenters, prob, dprob = getDegreeDistr(dfdegrees['degrees'])
        df = pd.DataFrame({'binCenters':binCenters, 'prob':prob, 'dprob':dprob})
        if toFile:
            call(f'mkdir -p {processedDataPath}', shell=True)
            df.to_csv(processedDataPath + '/' + distrFilename, index=False)
    return df

def plotDegreeDistr_manyir_oneDeltat(N, arena_r, irs, loops, poisson=False):
    fig, ax = plt.subplots()
    for ir in irs:
        dfDistr = getDegreeDistrKilombo(N, arena_r, ir, loops)
        line, = plt.plot(dfDistr['binCenters'], dfDistr['prob'], label=f'$r_i = {ir}$', marker='.', lw=0.7, ls=':')
        # if poisson ...
    ax.set(xlabel='Degree, $k$', ylabel='$P(k)$')
    fig.legend(loc=(0.7, 0.6), fontsize=9)
    fig.text(0.3, 0.97, f'N = {N}, $r_a = {arena_r}$, $\Delta t = {loops}$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'degreeDistr_N_{N}_ar_{arena_r}_loops_{loops}.png')

def MollyReedCriterion(N, arena_r, irs, loops_l, quenched=False):
    fig, ax = plt.subplots()
    # theoretical line:
    for loops in loops_l:
        mrFractions, averages = [], []
        for ir in irs:
            rawDataFilename = getConfigsPath() + '/raw_data/' + f'degrees_N_{N}_ar_{arena_r}_ir_{ir}_loops_{loops}.parquet'
            if not os.path.exists(rawDataFilename):
                getDegreesAllTraj(N, arena_r, ir, loops)
            dfdegrees = pd.read_parquet(rawDataFilename)
            dfdegrees['degrees_squared'] = dfdegrees['degrees']**2
            avgDeg, avgDegSq = np.mean(dfdegrees['degrees']), np.mean(dfdegrees['degrees_squared'])
            mrFractions.append(avgDegSq/avgDeg), averages.append(avgDeg)
        line, = ax.plot(irs, mrFractions, label=f'$\Delta t = {loops}$', lw=0.7)
        ax.plot(irs, [avg+1 for avg in averages], color=line.get_color(), ls=':', lw=0.7)
    if quenched:
        mrFractions, averages, irs_q = [], [], []
        exclusion_r, pushLabel = 1.5, 'nopush'
        for ir in irs:
            rawDataFilename_q = getExternalSSDpath() + f'/quenched_configs/{N}_bots/raw_data/degrees_N_{N}_ar_{arena_r+1.5}_er_{exclusion_r}_ir_{ir}_{pushLabel}.parquet'
            if not os.path.exists(rawDataFilename_q):
                print(f'Quenched degrees raw data does not exist for ir = {ir}')
            else:
                dfdegrees_q = pd.read_parquet(rawDataFilename_q)
                dfdegrees_q['degrees_squared'] = dfdegrees_q['degrees']**2
                avgDeg, avgDegSq = np.mean(dfdegrees_q['degrees']), np.mean(dfdegrees_q['degrees_squared'])
                mrFractions.append(avgDegSq/avgDeg), averages.append(avgDeg), irs_q.append(ir)
        ax.plot(irs_q, mrFractions, label='Quenched', color='xkcd:black', lw=0.7)
        ax.plot(irs_q, [avg+1 for avg in averages], color='xkcd:black', ls=':', lw=0.7)
    ax.axhline(2, lw=0.7, color='xkcd:gray')
    ax.set(xlabel='$r_i$', ylabel=r'$\langle k^{2} \rangle / \langle k \rangle$')
    fig.legend(loc=(0.25, 0.65), fontsize=9)
    fig.tight_layout()
    fig.savefig(f'MollyReedCriterion_N_{N}_ar_{arena_r}.png')


# MEAN CLUSTER SIZE
def computeMeanClusterSize(N, arena_r, interac_r, loops, maxCicles):
    """
    computes the mean cluster size for specific conditions: N, ar, ir, loops...
    """
    rawDataFilename = getConfigsPath() + '/raw_data/' + f'comSizesWoGc_N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet'
    df = pd.read_parquet(rawDataFilename)
    cicles = pd.unique(df['cicleID'])
    if len(cicles) > maxCicles:
        sep = int(len(cicles)/maxCicles)
        ciclesToUse = list(cicles)[::sep]
        ciclesToUse = sample(ciclesToUse, k=maxCicles)
        ciclesToUse.sort()
    else:
        ciclesToUse = cicles
    dfaux = df.query('cicleID in @ciclesToUse').copy()
    dfaux['comSizes_sq'] = dfaux['comSizes']**2
    a = sum(dfaux['comSizes'])
    b = sum(dfaux['comSizes_sq'])
    try:
        mcs = b/a
    except ZeroDivisionError:
        mcs = float('nan')
    return mcs

def getMeanClusterSize_ir(N, arena_r, loops, irs, maxCicles):
    """
    gets the MCS along a set of interaction radius, for fixed N, ar, loops
    """
    filename = getConfigsPath() + f'/processed_data/meanClusterSize_N_{N}_ar_{arena_r}_ir_loops_{loops}.csv'
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        missing_irs = [ir for ir in irs if ir not in list(df['interac_r'])]
        if missing_irs:
            mcs_l = []
            for ir in missing_irs:
                mcs = computeMeanClusterSize(N, arena_r, ir, loops, maxCicles)
                mcs_l.append(mcs)
            df_missing_irs = pd.DataFrame({'interac_r':missing_irs, 'mcs':mcs_l})
            df = pd.concat([df, df_missing_irs], ignore_index=True)
            df = df.sort_values(by='interac_r')
            df.to_csv(filename, index=False)
    else:  
        mcs_l = []
        for ir in irs:
            mcs = computeMeanClusterSize(N, arena_r, ir, loops, maxCicles)
            mcs_l.append(mcs)
        df = pd.DataFrame({'interac_r':irs, 'mcs':mcs_l})
        df.to_csv(filename, index=False)
    return df

def plotMeanClusterSize(N, arena_r, loops_l, maxCicles, quenched=False):
    fig, ax = plt.subplots()
    ax.set(xlabel='$r_i$', ylabel='MCS')
    for loops in loops_l:
        irs = availableIrs(N, arena_r, loops)
        dfmcs = getMeanClusterSize_ir(N, arena_r, loops, irs, maxCicles)
        ax.plot(dfmcs['interac_r'], dfmcs['mcs'], label = f'{loops}', marker='.', lw=0.7)
    if quenched:
        dfmcs_q = pd.read_csv(f'quenched_results/MeanClusterSize_v0_nopush_N_{N}_ar_{arena_r+1.5}_er_1.5.csv')
        ax.plot(dfmcs_q['interac_r'], dfmcs_q['mcs'], marker='.', ls='--', lw=0.7, color='k', label='Quenched')
    fig.legend(title='$\Delta t$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'meanClusterSize_N_{N}_ar_{arena_r}.png')










if __name__ == '__main__':
    # plotDegreeDistr_manyir_oneDeltat(35, 18.5, [3.5, 3.75, 5.0, 8.0], 800)
    # MollyReedCriterion(35, 18.5, [4.0, 5.0, 6.0, 7.0, 8.0], [0, 800], quenched=True)
    N, ar, loops = 35, 18.5, 800
    plotMeanClusterSize(N, ar, [0, 400, 800], 100, quenched=True)

