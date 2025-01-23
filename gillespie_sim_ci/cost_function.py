import numpy as np
from subprocess import call
import argparse
import os
import pandas as pd
from math import isnan
import random
import glob
import sys
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    resPath = extSSDpath + getProjectFoldername() + '/gillespie_sim_ci/results'
else:
    resPath = '/results'
    print('Forgot the SSD!!!!!')


def search_time_useStatDif(time, evo, statVal: float, statTime: float):
    evo_dif_to_stat = abs(evo - statVal)
    evo_rel_dif_to_stat = abs(evo - statVal)/statVal
    avgdif = np.average(evo_dif_to_stat[time >= statTime])
    # times_below_avgdif = time[evo_dif_to_stat < avgdif]
    times_rel_dif_overX = time[evo_rel_dif_to_stat >= 0.9]
    if len(times_rel_dif_overX) > 0:
        mintss = max(times_rel_dif_overX)
    else:
        mintss = 0
    # if statVal is very small do not consider the relative difference as it may rocket up many times...
    if statVal > 0.1:
        refinedTimes = time[(evo_dif_to_stat < avgdif) & (time > mintss) & (time > 2.0)]
    else:
        refinedTimes = time[(evo_dif_to_stat < avgdif) & (time > 2.0)]
    # finally...
    # initially i did this...
    # if len(refinedTimes) > 3:
    #     max_times_to_use = 3
    # else:
    #     max_times_to_use = len(refinedTimes)
    # tss = np.average(refinedTimes[0:max_times_to_use])
    # but let's only use the first time from refined times...
    tss = refinedTimes[0]
    return tss


def execSims_for_time_evos(pis, qs, l, lci, ci_kwargs, N, ic, maxTime, Nrea):
    pichainExec = ','.join([str(pi) for pi in pis])
    qchainExec = ','.join([str(q) for q in qs])
    ci_kwargs_chainExec = ','.join([str(cikw) for cikw in ci_kwargs])
    # simCall = f'python LES_model_gill.py -pis {pichainExec} -qs {qchainExec} -l {l} -lci {lci} -ci_kwargs {ci_kwargs_chainExec} '
    # simCall += f'-N {N} -maxTime {maxTime} -Nrea {Nrea} -ic {ic} --time_evo'
    simCall = f'python LES_model_gill_numba.py -pis {pichainExec} -qs {qchainExec} -l {l} -lci {lci} -ci_kwargs {ci_kwargs_chainExec} '
    simCall += f'-N {N} -maxTime {maxTime} -Nrea {Nrea} -ic {ic}'
    call(simCall, shell=True)


def get_data_for_cost_func(h, pis, qs, l, lci, ci_kwargs, N, ic, maxTime=100.0, Nrea=100, execSim=False, keepData=False, smoothEvo = False):
    """
    keepData only works when execSim==True; then if keepData=True, Nrea simulations are executed and added to the already existing folder

    --- smoothEvo ---
    since I modified the simulation code to use numba, I aslo printed less points there from the time evolution
    consequently there is no need to smooth out the time evolutions now; smooth_evo=False
    """
    pichain = '_'.join([str(pi) for pi in pis])
    qchain = '_'.join([str(q) for q in qs])
    ci_kwargs_chain = '_'.join([str(cikw) for cikw in ci_kwargs])
    evoName = f'sim_results_evos_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}_N_{N}_ic_{ic}'
    ## firewall for the keepData feature ## if True but it actually does not exists, set parameter to False and go on
    if keepData:
        if not os.path.exists(f'{resPath}/{evoName}'):
            keepData = False
    #####
    if execSim: # make it mandatory to execute simulations, even if evos folder already exists, and add to or replace the old ones
        execSims_for_time_evos(pis, qs, l, lci, ci_kwargs, N, ic, maxTime, Nrea)
        call(f'tar -xzf {evoName}.tar.gz', shell=True)
        call(f'rm {evoName}.tar.gz', shell=True)
        if keepData and os.path.exists(f'{resPath}/{evoName}'):
            existingEvos = len(glob.glob(f'{resPath}/{evoName}/*'))
            for i in range(Nrea): # first rename all
                call(f'mv {evoName}/time_evo_rea_{i}.csv {evoName}/time_evo_rea_{i+existingEvos}.csv', shell=True)
            for i in range(Nrea): # then move all
                call(f'mv {evoName}/time_evo_rea_{i+existingEvos}.csv {resPath}/{evoName}/', shell=True)
            call(f'rm -r {evoName}', shell=True)
        else:
            existingEvos = 0
            # before moving, chech if directory already exists and if so remove it:
            if os.path.exists(f'{resPath}/{evoName}'):
                call(f'rm -r {resPath}/{evoName}', shell=True)
            call(f'mv {evoName} {resPath}/', shell=True)
    #####
    if os.path.exists(os.path.exists(evoName)): # folder exits so it can be used
        evoFiles = glob.glob(f'{resPath}/{evoName}/*')
    else:
        print('No evos folder found, please execute with execSim=True')
        return
    tssMax, tssFs, statDataPool = [], {}, {}
    for k in range(len(pis)+1):
        tssFs[f'f{k}'], statDataPool[f'f{k}'] = [], []
    statTime = 0.8*maxTime
    if execSim and keepData and os.path.exists(f'{resPath}/{evoName}'):
        iterFiles = range(existingEvos, existingEvos+Nrea)
    else:
        iterFiles = range(len(evoFiles))
    for file_i in iterFiles:
        # if i%10 == 0:
        #     print(f'analyzing file {i}')
        f = f'{resPath}/{evoName}/time_evo_rea_{file_i}.csv'
        tevo = pd.read_csv(f)
        tssRea = []
        for k in range(len(pis)+1):
            statVal = np.average(tevo.query('time > @statTime')[f'f{k}'])
            if smoothEvo:
                fevo_smoothed = []
                for i in range(int(maxTime/h)):
                    tmin, tmax = h*i, h*(i+1)
                    fblock = np.average(tevo.query('time >= @tmin and time < @tmax')[f'f{k}'])
                    fevo_smoothed.append(fblock)
                times_smooth = np.arange(0,maxTime,h)
                tss = search_time_useStatDif(times_smooth, fevo_smoothed, statVal, statTime)
            else:
                tss = search_time_useStatDif(np.array(tevo['time']), np.array(tevo[f'f{k}']), statVal, statTime)
            tssFs[f'f{k}'].append(tss), tssRea.append(tss)
        tssRea = [t for t in tssRea if not isnan(t)]
        if len(tssRea) > 0:
            tssRea = sorted(tssRea)
            tssMaxRea = tssRea.pop() # already removing the max time from the list...
            tssMax.append(tssMaxRea)
            # get 2000 uniformly distributed points in the stationary state
            tevoAux = tevo.query('time >= @tssMaxRea')
            len_statData = len(tevoAux)
            while len_statData < 2000 and len(tssRea) > 0:
                # print(f'could not get 2000 different ss values for {f}')
                # tssAlt = sorted(tssRea, reverse=True)[1]
                tssAlt = tssRea.pop()
                tevoAux = tevo.query('time >= @tssAlt')
            len_statData = len(tevoAux)
            if len_statData < 2000:
                print(f'could not get 2000 different ss values for {f}')
            index_statData = np.linspace(tevoAux.index[0], tevoAux.index[-1], 2000, dtype=int)
            tevoAux = tevo.query('index in @index_statData')
            for k in range(len(pis)+1):
                # statDataPool[f'f{k}'].extend(list(tevo.query('time >= @tssMaxRea')[f'f{k}'])[::3])
                statDataPool[f'f{k}'].extend(list(tevoAux[f'f{k}']))
        else:
            tssMax.append(float('nan'))
    # save data: csv? npy?
    tssFs['tssMax'] = tssMax
    tssDf = pd.DataFrame(tssFs)
    fcolumns = [col for col in tssDf.columns if col.startswith('f')]
    tssDf['tssAvg'] = tssDf[fcolumns].sum(axis=1)/3
    statDataPool = pd.DataFrame(statDataPool)
    if execSim and keepData:
        old_tssDf = pd.read_csv(f'{resPath}/tss_from_sim_results_evos_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}_N_{N}_ic_{ic}.csv')
        old_tssDf = pd.concat([old_tssDf, tssDf], ignore_index=True)
        old_tssDf.to_csv(f'{resPath}/tss_from_sim_results_evos_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}_N_{N}_ic_{ic}.csv', index=False)
        old_statDataPool = pd.read_csv(f'{resPath}/ss_data_from_sim_results_evos_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}_N_{N}_ic_{ic}.csv')
        old_statDataPool = pd.concat([old_statDataPool, statDataPool], ignore_index=True)
        old_statDataPool.to_csv(f'{resPath}/ss_data_from_sim_results_evos_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}_N_{N}_ic_{ic}.csv', index=False)
    else:
        tssDf.to_csv(f'{resPath}/tss_from_sim_results_evos_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}_N_{N}_ic_{ic}.csv', index=False)
        statDataPool.to_csv(f'{resPath}/ss_data_from_sim_results_evos_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}_N_{N}_ic_{ic}.csv', index=False)
    return tssMax, statDataPool


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    h = 1.0
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-l', help='lambda', type=float)
    parser.add_argument('-lci', help='lambda ci', type=float)
    parser.add_argument('-ci_kwargs', help='(cimode; ci_x0, ci_a)', type=lambda s: [float(item) for item in s.split(',')], default=[0, ])
    parser.add_argument('-N', type=int, help='Number of agents')
    parser.add_argument('-maxTime', type=float, help='simulation time')
    parser.add_argument('-Nrea', type=int, help='Number of realizations')
    parser.add_argument('-ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    args = parser.parse_args()
    pis, qs, l, lci, ci_kwargs, N, maxTime, Nrea, ic = args.pis, args.qs, args.l, args.lci, args.ci_kwargs, args.N, args.maxTime, args.Nrea, args.ic
    ci_kwargs[0] = int(ci_kwargs[0])
    # get_data_for_cost_func(h, pis, qs, l, lci, ci_kwargs, N, ic, maxTime, Nrea, execSim=True, keepData=True)
    # get_data_for_cost_func(h, pis, qs, l, lci, ci_kwargs, N, ic, maxTime, Nrea, execSim=False)
    get_data_for_cost_func(h, pis, qs, l, lci, ci_kwargs, N, ic, maxTime, Nrea, execSim=True)
    