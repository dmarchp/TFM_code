import numpy as np
import pandas as pd
from numba import jit
from datetime import datetime
import argparse
from subprocess import call
import sys
sys.path.append('../../')
from package_global_functions import *

#### got to think whether is it ok to save all timesteps of the time evos... it takes so much space

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    resPath = extSSDpath + getProjectFoldername() + 'non_lin_models/gillespie_non_lin_model/results'
else:
    resPath = '/results'

# def gillespieStep(state, vecsChange, timeLeft):
@jit
def gillespieStep(state, pis, qs, l1, l2, N, vecsChange, timeLeft, rng):
    probsChange = []
    for i in range(Nsites):
        # discovery of option i+1: (options are labelled 1,2... 0 is the uncommitted state)
        probsChange.append(state[0]*pis[0])
        # abandonment of option i+1:
        probsChange.append(state[i+1]*1/qs[i])
        # recruitment by a single peer:
        probsChange.append(l1*state[0]*state[i+1]/N)
        # recruitment by two peers:
        probsChange.append(l2*state[0]*state[i+1]**2/(N*N))
        #######
    probSum = sum(probsChange)
    timeInterval = rng.exponential(1/probSum)
    if timeInterval > timeLeft:
        return True, timeLeft
    # tower sample to select the next reaction:
    probsChange = [prob/probSum for prob in probsChange]
    indexSelReac = -1
    randReac = 0.0
    while randReac == 0.0:
        randReac = rng.random()
    bottom = 0.0
    for i,prob in enumerate(probsChange):
        if (randReac >= bottom and randReac <(bottom+prob)):
            indexSelReac = i
            break
        bottom += prob
    # if indexSelReac == -1:
    #     print('Problem in selectin a reaction!')
    # try:
    #     state += np.array(vecsChange[indexSelReac])
    # except IndexError:
    #     print(indexSelReac)
    #     print(probsChange)
    #     print(randReac)
    #     print(state)
    #     input('enter ')
    state += np.array(vecsChange[indexSelReac])
    return False, timeInterval


def gillespieSim(initial_state, save_time_evo=False, save_time_evo_ts = 1, avg_last_perc=0.2):
    # avg_last_perc = fraction of maxTime to save data for avgs
    # global Nsites
    state = np.array(initial_state)
    t = 0
    # Creating the list of vector of change
    vecsChange = []
    for i in range(1,Nsites+1):
        # possible transitions: discovery, abandonment, recruitment by 1 peer, recruitment by 2 peers
        for j in range(4): # disc, aband, recruit1, recruit2 for site i
            vec_change = [0]*(Nsites+1)
            if j==0 or j==2 or j==3: # discovery, recruitment1, recruitment2
                vec_change[0], vec_change[i] = -1, +1
            # if j==1 or j==3: # abandoment
            else:
                vec_change[0], vec_change[i] = +1, -1
            vecsChange.append(vec_change)
    if save_time_evo: # save initial condition
        time_evo = [[0.0],]
        aux = [[state[i]/N, ] for i in range(Nsites+1)]
        time_evo.extend(aux)
        t_since_last_save_ts = 0.0
    ######################## START SIMULATION LOOP ########################
    state_ss_avg = [[] for i in range(Nsites+1)]
    while t < maxTime:
        # prevState = copy.deepcopy(state)
        simFinished, timeStep = gillespieStep(state, vecsChange, maxTime-t)
        t += timeStep
        # Save whole time evolution:
        if save_time_evo:
            t_since_last_save_ts += timeStep
            if t_since_last_save_ts > save_time_evo_ts:
                time_evo[0].append(t)
                for i in range(1,Nsites+2):
                    time_evo[i].append(state[i-1]/N)
                t_since_last_save_ts = 0.0
        # Save values to compute stationary state averages:
        if t > maxTime*(1-avg_last_perc):
            for i in range(Nsites+1):
                state_ss_avg[i].append(state[i])
        if simFinished:
            break
    ######################## FINISH SIMULATION LOOP ########################
    # before converting values to average, save them for the SS distribution, if required:
    if saveSSdata:
        for i in range(Nsites+1):
            ssDataPool[i].extend(state_ss_avg[i][-2000:]) # only use the last 2000 values, so every realization contributes the same
    # now get the average values for this realization
    for i in range(Nsites+1):
        state_ss_avg[i] = np.average(state_ss_avg[i])
    # return final state, final SS average, and time evolution (if required)
    if save_time_evo:
        dfevo = pd.DataFrame({'time':time_evo[0]})
        for i in range(1,Nsites+2):
            dfevo[f'f{i-1}'] = time_evo[i]
        return state, state_ss_avg, dfevo
    else:
        return state, state_ss_avg
    
@jit
def gillespieSim_numba(initial_state, pis, qs, l1, l2, N, maxTime, rng, save_time_evo=True, save_time_evo_ts_tuple = (0.2, 1)):
    ### save_time_evo_ts_tuple = (time step when t<=10, time step when t > 10)
    state = np.array(initial_state)
    t = 0.0
    # Creating the list of vector of change
    vecsChange = []
    for i in range(1,Nsites+1):
        # possible transitions: discovery, abandonment, recruitment by 1 peer, recruitment by 2 peers
        for j in range(4): # disc, aband, recruit1, recruit2 for site i
            vec_change = [0]*(Nsites+1)
            if j==0 or j==2 or j==3: # discovery, recruitment1, recruitment2
                vec_change[0], vec_change[i] = -1, +1
            # if j==1 or j==3: # abandoment
            else:
                vec_change[0], vec_change[i] = +1, -1
            vecsChange.append(vec_change)
    if save_time_evo: # save initial condition
        time_evo = [[0.0],]
        aux = [[state[i]/N, ] for i in range(Nsites+1)]
        time_evo.extend(aux)
        t_since_last_save_ts = 0.0
    ######################## START SIMULATION LOOP ########################
    while t < maxTime:
        # prevState = copy.deepcopy(state)
        simFinished, timeStep = gillespieStep(state, pis, qs, l1, l2, N, vecsChange, maxTime-t, rng)
        t = t + timeStep
        # Save whole time evolution:
        if t >= 10:
            save_time_evo_ts = save_time_evo_ts_tuple[1]
        else:
            save_time_evo_ts = save_time_evo_ts_tuple[0]
        if save_time_evo:
            t_since_last_save_ts = t_since_last_save_ts + timeStep
            if t_since_last_save_ts > save_time_evo_ts:
                time_evo[0].append(t)
                for i in range(1,Nsites+2):
                    time_evo[i].append(state[i-1]/N)
                t_since_last_save_ts = 0.0
        if simFinished:
            break
    ######################## FINISH SIMULATION LOOP ########################
    if save_time_evo:
        # numba does not suppor pandas nor dictionaries; the dataframe needs to be generated outside the function...
        # dfevo = pd.DataFrame({'time':time_evo[0]})
        # for i in range(1,Nsites+2):
            # dfevo[f'f{i-1}'] = time_evo[i]
        return state, time_evo
    # else:
    #     return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-l1', help='lambda for linear recruitment (1 peer)', type=float)
    parser.add_argument('-l2', help='lambda for quadractic recruitment (2 peers)', type=float)
    parser.add_argument('-N', type=int, help='Number of agents')
    parser.add_argument('-maxTime', type=float, help='simulation time')
    parser.add_argument('-Nrea', type=int, help='Number of realizations')
    parser.add_argument('-ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    # boolean arguments 
    parser.add_argument('--final_state', type=bool, help='Print each realization final state', action=argparse.BooleanOptionalAction)
    parser.add_argument('--ss_data', type=bool, help='Save SS values in a dataframe', action=argparse.BooleanOptionalAction)
    parser.add_argument('--time_evo', type=bool, help='Save time evolutions as df', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    pis, qs, l1, l2, N, maxTime, Nrea, ic = args.pis, args.qs, args.l1, args.l2, args.N, args.maxTime, args.Nrea, args.ic
    saveTimeEvo, printFinalState, saveSSdata = args.time_evo, args.final_state, args.ss_data
    # fuck it
    saveTimeEvo = True
    if len(pis) != len(qs):
        print('Input number of pis different from qualities. Aborting.')
        exit()
    Nsites = len(pis)
    #### assing the initial condition ####
    bots_per_site = prepare_ic(N, Nsites, ic)
    #### initiate random number generator
    ## old way; should not be used: ##
    # rnd_seed = int(datetime.now().timestamp())
    # np.random.seed(rnd_seed)
    ## better instead used this: this generator is globaly seen by the gillespie step function (is/WAS passed as an argument to the gillespie step function) ##
    rng = np.random.default_rng(seed=int(datetime.now().timestamp()))
    #### RUN GILLESPIE SIMULATIONS ####
    fsavg_rea = [[] for i in range(Nsites+1)]
    pichain = '_'.join([str(pi) for pi in pis])
    qchain = '_'.join([str(q) for q in qs])
    if saveTimeEvo:
        evosFolder = f'sim_results_evos_pis_{pichain}_qs_{qchain}_l1_{l1}_l2_{l2}_N_{N}_ic_{ic}'
        call(f'mkdir -p {evosFolder}/', shell=True)
    if saveSSdata:
        ssData_fname = f'sim_pis_{pichain}_qs_{qchain}_l1_{l1}_l2_{l2}_N_{N}_ic_{ic}.csv'
        ssDataPool = [[] for i in range(Nsites+1)]
    ##### START REALIZATIONS LOOP #####
    for i in range(Nrea):
        if saveTimeEvo:
            # finalState, ssAvgState, dfevo = gillespieSim(bots_per_site, save_time_evo=True)
            ##### using numba....
            finalState, time_evo = gillespieSim_numba(bots_per_site, pis, qs, l1, l2, N, maxTime, rng, save_time_evo=True)
            dfevo = pd.DataFrame({'time':time_evo[0]})
            for j in range(1,Nsites+2):
                dfevo[f'f{j-1}'] = time_evo[j]
            dfevo.to_csv(f'{evosFolder}/time_evo_rea_{i}.csv', index=False)
        else:
            # finalState, ssAvgState = gillespieSim(bots_per_site, pis, qs, l1, l2, N, maxTime, rng)
            finalState = gillespieSim_numba(bots_per_site, pis, qs, l1, l2, N, maxTime, rng)
        if printFinalState:
            finalStatefs = [s/N for s in finalState]
            # ssAvgStatefs = [s/N for s in ssAvgState]
            # print(f'Final State: {finalStatefs}     SS Averages: {ssAvgStatefs}')
            print(f'Final State: {finalStatefs}')
    ##### END REALIZATIONS LOOP #####

    ### save stationary state distribution:
    if saveSSdata:
        if not os.path.exists(resPath):
            call(f'mkdir -p {resPath}', shell=True)
        ssDF = {}
        ssDataPool = np.array(ssDataPool)/N
        for i in range(Nsites+1):
            ssDF[f'f{i}'] = ssDataPool[i]
        ssDF = pd.DataFrame(ssDF)
        ssDF.to_csv(resPath + '/' + ssData_fname, index=False)
    
    if saveTimeEvo:
        call(f'tar -czf {evosFolder}.tar.gz {evosFolder}', shell=True)
        call(f'rm -r {evosFolder}', shell=True)