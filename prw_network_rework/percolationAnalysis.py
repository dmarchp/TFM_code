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
from scipy.optimize import curve_fit
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

# COMMUNITY SIZES DISTRIBUTION:
def powerLaw(x,a,b):
    return a*x**b

# funció gegant en que tot es fa a dins de la funció (compute->get->plot), a difèrencia del MCS o avg giant comp.
# també calculo la P(s) del cas quenched aqui inclús...
# potser ho hauria de trencar tot en trossets, o no
def plotComSizesDistr_dif_loops(N: int, ar: float, irs: "list[float]", loopsList: "list[int]", quench_ir: float, logBins: int, 
                           excludeGiantComp=True, dataToFile = False, fitPL=False, fitPLindex=0):
    '''
    comutes the ~power law~ like figure of the number of com of sizes s vs size s.
    as each loop has a different critical percolation radius, a list irs has to be provided
    fitPLindex: data index from which to fit the power law
    '''
    gcLabel = 'excludedGC' if excludeGiantComp else ''
    fig, ax = plt.subplots()
    ax.set(xlabel='s', ylabel='P(s)', xscale='log', yscale='log')
    if N == 492:
        ax.set(ylim=(1e-6,None))
    loop_markers = ['2', '+', '^']
    for ir, loops, lm in zip(irs, loopsList, loop_markers):
        if excludeGiantComp:
            rawDataFilename = getConfigsPath() + '/raw_data/' + f'comSizesWoGc_N_{N}_ar_{ar}_ir_{ir}_loops_{loops}.parquet'
        else:
            rawDataFilename = getConfigsPath() + '/raw_data/' + f'comSizes_N_{N}_ar_{ar}_ir_{ir}_loops_{loops}.parquet'
        df = pd.read_parquet(rawDataFilename)
        df = comSizesDiscard(df, N, ir, loops)
        binLims = np.geomspace(1,N-1,logBins)
        binCenters = np.sqrt(binLims[1:]*binLims[:-1])
        binCenters, pdf, stdpdf = hist1D(df['comSizes'], binLims, binCenters, isPDF=True)
        if dataToFile:
            df = pd.DataFrame({'comSize':binCenters, 'prob':pdf, 'dprob':stdpdf})
            df.to_csv(getConfigsPath() + f'/processed_data/comSizesProbDistr_N_{N}_ar_{ar}_ir_{ir}_loops_{loops}.csv', index=False)
        # ax.plot(binCenters, pdf, ls='None', marker=lm, label=rf'$\Delta t = {loops}$, $r_{{int}}^{{*}} = {ir}$')
        line = ax.errorbar(binCenters, pdf, stdpdf, marker=lm, ls='None', alpha=0.8, elinewidth=0.8, capsize=2, label=rf'$\Delta t = {loops}$, $r_{{int}}^{{*}} = {ir}$')
        if fitPL:
            # tot això no fa falta perquè hist1D ja em borra els binCenters amb pdf==0
            # pdfZeroIndex = np.where(pdf == 0.0)[0]
            # if pdfZeroIndex.size == 0:
            #     pdfZeroIndex = None
            # else:
            #     pdfZeroIndex = pdfZeroIndex[0]
            # binCenters, pdf = binCenters[fitPLindex:pdfZeroIndex], pdf[fitPLindex:pdfZeroIndex]
            binCenters, pdf = binCenters[fitPLindex[0]:fitPLindex[1]], pdf[fitPLindex[0]:fitPLindex[1]]
            paramfit, covfit = curve_fit(powerLaw, binCenters, pdf)
            fit = powerLaw(binCenters, *paramfit)
            ax.plot(binCenters, fit, ls='--', alpha=0.5, color=line.lines[0].get_color(), lw=0.7)
            ax.text(0.1, 0.4-irs.index(ir)*0.05, rf'{round(paramfit[0],3)} s**({round(paramfit[1],3)})', fontsize=8, color=line.lines[0].get_color(), transform=ax.transAxes)
    if quench_ir:
        pathSSD = getExternalSSDpath() + f'/quenched_configs/{N}_bots/raw_data'
        if excludeGiantComp:
            rawDataFilename = pathSSD + f'/comSizesWoGc_N_{N}_ar_{ar+1.5}_er_1.5_ir_{quench_ir}_nopush.parquet'
        else:
            rawDataFilename = pathSSD + f'/comSizes_N_{N}_ar_{ar+1.5}_er_1.5_ir_{quench_ir}_nopush.parquet'
        df = pd.read_parquet(rawDataFilename)
        binLims = np.geomspace(1,N-1,logBins)
        binCenters = np.sqrt(binLims[1:]*binLims[:-1])
        binCenters, pdf, stdpdf = hist1D(df['comSizes'], binLims, binCenters, isPDF=True)
        if dataToFile:
            df = pd.DataFrame({'comSize':binCenters, 'prob':pdf, 'dprob':stdpdf})
            df.to_csv(getExternalSSDpath() + f'/quenched_configs/{N}_bots/processed_data/comSizesProbDistr_N_{N}_ar_{ar+1.5}_er_1.5_ir_{quench_ir}_nopush.csv')
        ax.errorbar(binCenters, pdf, stdpdf, marker='.', ls='None', color='k', alpha=0.8, elinewidth=0.8, capsize=2, label=f'Quenched, $r_{{int}}^* = {quench_ir}$')
        if fitPL:
            binCenters, pdf = binCenters[fitPLindex[0]:fitPLindex[1]], pdf[fitPLindex[0]:fitPLindex[1]]
            paramfit, covfit = curve_fit(powerLaw, binCenters, pdf)
            fit = powerLaw(binCenters, *paramfit)
            ax.plot(binCenters, fit, ls='--', alpha=0.5, color='k', lw=0.7)
            ax.text(0.1, 0.25, rf'{round(paramfit[0],3)} s**({round(paramfit[1],3)})', fontsize=8, color='k', transform=ax.transAxes)
    fig.text(0.35, 0.97, f'$excludeGiantComp = {excludeGiantComp}$')
    fig.legend(fontsize=9, loc=(0.65,0.7)) #  
    fig.tight_layout()
    fig.savefig(f'comSizesProbs_difLoops_N_{N}_ar_{ar}_kilombo_{gcLabel}.png')

def comSizesDiscard(df, N, interac_r, loops):
    # apaño cutre: discard the same you discard when computing the MCS!!
    if N == 35:
        if loops == 0:
            df = df.query('not (trajID == 8 and cicleID in [7408, 7409, 7410])')
        if loops == 400:
            df = df.query('not (trajID == 2 and cicleID == 6)')
        if loops == 800:
            if interac_r == 6.0:
                df = df.query('not (trajID == 2 and cicleID == 3)')
            elif interac_r == 5.0:
                #discarded = len(df.query('comSizes < 20'))
                #print(f'You are discarding {discarded} configurations')
                #df = df.query('comSizes >= 20')
                df = df.query("""not ((trajID == 10 and cicleID == 20) and (trajID == 4 and cicleID == 95) \
                            and (trajID == 9 and cicleID == 50) and (trajID == 10 and cicleID == 98) and (trajID == 8 and cicleID == 49) \
                            and (trajID == 2 and cicleID == 3) and (trajID == 8 and cicleID == 84) and (trajID == 2 and cicleID == 57) \
                            and (trajID == 5 and cicleID == 45) and (trajID == 5 and cicleID == 98) and (trajID == 7 and cicleID == 16))""")
    if N == 492:
        if loops == 800:
            if interac_r == 4.5:
                df = df.query('not (trajID == 1 and cicleID == 0)')
    return df

# MEAN CLUSTER SIZE
def computeMeanClusterSize(N, arena_r, interac_r, loops, maxCicles):
    """
    computes the mean cluster size for specific conditions: N, ar, ir, loops...
    maxCicles per trajectory to use
    """
    rawDataFilename = getConfigsPath() + '/raw_data/' + f'comSizesWoGc_N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet'
    df = pd.read_parquet(rawDataFilename)
    df = comSizesDiscard(df, N, interac_r, loops)
    trajs = pd.unique(df['trajID'])
    comSizes = []
    for traj in list(trajs):
        dftraj = df.query('trajID == @traj')
        cicles = pd.unique(dftraj['cicleID'])
        if len(cicles) > maxCicles:
            sep = int(len(cicles)/maxCicles)
            ciclesToUse = list(cicles)[::sep]
            ciclesToUse = sample(ciclesToUse, k=maxCicles)
            ciclesToUse.sort()
        else:
            ciclesToUse = cicles
        dftraj = df.query('cicleID in @ciclesToUse').copy()
        comSizes.extend(list(dftraj['comSizes']))
    comSizes = np.array(comSizes)
    a = np.sum(comSizes)
    b = np.sum(comSizes**2)
    try:
        mcs = b/a
    except ZeroDivisionError or RuntimeWarning:
        mcs = float('nan')
    return mcs

def getMeanClusterSize_ir(N, arena_r, loops, irs, maxCicles):
    """
    gets the MCS along a set of interaction radius, for fixed N, ar, loops
    maxCicles per trajectory
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
        pathSSD = getExternalSSDpath() + f'/quenched_configs/{N}_bots/processed_data'
        filename_q = f'meanClusterSize_nopush_N_{N}_ar_{arena_r+1.5}_er_1.5.csv'
        pathLocal = 'quenched_results'
        if os.path.exists(pathSSD+'/'+filename_q):
            dfmcs_q = pd.read_csv(pathSSD+'/'+filename_q)
        elif os.path.exists(pathLocal + '/' + filename_q):
            print('Using local file to plot the quenched MCS')
            dfmcs_q = pd.read_csv(pathLocal+'/'+filename_q)
        try:
            ax.plot(dfmcs_q['interac_r'], dfmcs_q['mcs'], marker='.', ls='--', lw=0.7, color='k', label='Quenched')
        except UnboundLocalError:
            print('There is no quenched MCS file!')
    fig.legend(title='$\Delta t$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'meanClusterSize_N_{N}_ar_{arena_r}.png')


# Average giant component:

def computeAvgGiantComp(N, arena_r, interac_r, loops, maxCicles):
    """
    computes the average giant component for fixed N, ar, ir, loops
    maxCicles per trajectory
    """
    rawDataFilename = getConfigsPath() + '/raw_data/' + f'comSizes_of_Gc__N_{N}_ar_{arena_r}_ir_{interac_r}_loops_{loops}.parquet'
    df = pd.read_parquet(rawDataFilename)
    df = comSizesDiscard(df, N, interac_r, loops)
    trajs = pd.unique(df['trajID'])
    comSizes = []
    for traj in list(trajs):
        dftraj = df.query('trajID == @traj')
        cicles = pd.unique(dftraj['cicleID'])
        if len(cicles) > maxCicles:
            sep = int(len(cicles)/maxCicles)
            ciclesToUse = list(cicles)[::sep]
            ciclesToUse = sample(ciclesToUse, k=maxCicles)
            ciclesToUse.sort()
        else:
            ciclesToUse = cicles
        dftraj = df.query('cicleID in @ciclesToUse').copy()
        comSizes.extend(list(dftraj['comSizes']))
    comSizes = np.array(comSizes)
    return np.average(comSizes), np.std(comSizes)

def getAvgGiantComp_ir(N, arena_r, loops, irs, maxCicles):
    """
    gets the average Giant Component along a set of interaction radius, for fixed N, ar, loops
    maxCicles per trajectory
    """
    filename = getConfigsPath() + f'/processed_data/avgGiantComp_{N}_ar_{arena_r}_ir_loops_{loops}.csv'
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        missing_irs = [ir for ir in irs if ir not in list(df['interac_r'])]
        if missing_irs:
            avgs, stds = [], []
            for ir in missing_irs:
                avg, std = computeAvgGiantComp(N, arena_r, ir, loops, maxCicles)
                avgs.append(avg), stds.append(std)
            df_missing_irs = pd.DataFrame({'interac_r':missing_irs, 'avg':avgs, 'std':stds})
            df = pd.concat([df, df_missing_irs], ignore_index=True)
            df = df.sort_values(by='interac_r')
            df.to_csv(filename, index=False)
    else:  
        avgs, stds = [], []
        for ir in irs:
            avg, std = computeAvgGiantComp(N, arena_r, ir, loops, maxCicles)
            avgs.append(avg), stds.append(std)
        df = pd.DataFrame({'interac_r':irs, 'avg':avgs, 'std':stds})
        df.to_csv(filename, index=False)
    return df

def plotAvgGiantComp(N, arena_r, loops_l, maxCicles, quenched=False):
    fig, ax = plt.subplots()
    ax.set(xlabel=r'$r_{int}$', ylabel='Avg Giant Comp')
    for loops in loops_l:
        irs = availableIrs(N, arena_r, loops)
        dfavgGc = getAvgGiantComp_ir(N, arena_r, loops, irs, maxCicles)
        # ax.plot(dfavgGc['interac_r'], dfavgGc['avg'], label = f'{loops}', marker='.', lw=0.7)
        ax.errorbar(dfavgGc['interac_r'], dfavgGc['avg'], dfavgGc['std'], fmt='.-', linewidth=0.8, elinewidth=0.5, capsize=2.0, label=f'{loops}')
    if quenched:
        pathSSD = getExternalSSDpath() + f'/quenched_configs/{N}_bots/processed_data'
        filename_q = f'avgGiantComp_nopush_N_{N}_ar_{arena_r+1.5}_er_1.5.csv'
        pathLocal = 'quenched_results'
        if os.path.exists(pathSSD+'/'+filename_q):
            dfavgGc_q = pd.read_csv(pathSSD+'/'+filename_q)
        elif os.path.exists(pathLocal + '/' + filename_q):
            print('Using local file to plot the quenched MCS')
            dfavgGc_q = pd.read_csv(pathLocal+'/'+filename_q)
        try:
            # ax.plot(dfavgGc_q['interac_r'], dfavgGc_q['avg'], marker='.', ls='--', lw=0.7, color='k', label='Quenched')
            ax.errorbar(dfavgGc_q['interac_r'], dfavgGc_q['avg'], dfavgGc_q['std'], fmt='.--k', linewidth=0.8, elinewidth=0.5, capsize=2.0, label=f'{loops}')
        except UnboundLocalError:
            print('There is no quenched MCS file!')
    fig.legend(title='$\Delta t$', fontsize=9, loc=(0.75, 0.2))
    fig.tight_layout()
    fig.savefig(f'avgGiantComp_N_{N}_ar_{arena_r}.png')





if __name__ == '__main__':
    # plotDegreeDistr_manyir_oneDeltat(35, 18.5, [3.5, 3.75, 5.0, 8.0], 800)
    # MollyReedCriterion(35, 18.5, [4.0, 5.0, 6.0, 7.0, 8.0], [0, 800], quenched=True)

    N, ar, loops = 35, 18.5, 800
    # plotMeanClusterSize(N, ar, [0, 400, 800], maxCicles=100, quenched=True)
    # plotAvgGiantComp(N, ar, [0, 400, 800], maxCicles=100, quenched=True)
    plotComSizesDistr_dif_loops(N, ar, [7.0, 5.0, 4.0], [0,400,800], 6.5, 15, fitPL=True, fitPLindex=(5,9), dataToFile=True)
    N, ar, loops = 492, 73.5, 800
    # plotMeanClusterSize(N, ar, [0, 400, 800], maxCicles=36, quenched=True)
    # plotAvgGiantComp(N, ar, [0, 400, 800], maxCicles=36, quenched=True)
    plotComSizesDistr_dif_loops(492, 73.5, [6.0, 4.5, 3.5], [0,400,800], 6.5, 25, fitPL=True, fitPLindex=(6,16), dataToFile=True)

