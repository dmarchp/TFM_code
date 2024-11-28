import numpy as np
from datetime import datetime
from numba import jit
import argparse
import copy
import sys
import os
from subprocess import call
sys.path.append('../')
from package_global_functions import *
# from more_sites import prepare_ic

# sample exec command if u feel lazy
# python LES_model_gill.py -pis 0.1,0.1 -qs 9.0,10.0 -l 0.6 -lci 1.0 -N 500 -maxTime 100.0 -Nrea 10 -ic N --time_evo_plot

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    resPath = extSSDpath + getProjectFoldername() + '/gillespie_sim_ci/results2'
else:
    resPath = '/results'

@jit
def cross_in_func(pop,ci_kwargs):
    ### kwargs ###
    # first: linear, sigmoid 1 or 2...
    # second: x0
    # third: a
    # fouth: make superior part of the sigmoid linear (True) or not
    if ci_kwargs[0] == 0 or ci_kwargs[0] == 'lin':
        return pop
    elif ci_kwargs[0] == 1 or ci_kwargs[0] == 'sigmoid1':
        x0 = ci_kwargs[1]
        a = ci_kwargs[2]
        cival = 1/(1+np.exp(-a*(pop-x0)))
        return cival
    elif ci_kwargs[0] == 2 or ci_kwargs[0] == 'sigmoid2':
        x0 = ci_kwargs[1]
        a = ci_kwargs[2]
        cival = pop/(1+np.exp(-a*(pop-x0)))
        return cival

@jit
def LESgillespieStep(state, pis, qs, l, lci, ci_kwargs, N, vecsChange, timeLeft, rng):
    probsChange = []
    for i in range(Nsites):
        # disocvery of option i+1:
        probsChange.append((1-l)*pis[i]*state[0])
        # abandonment of option i+1:
        probsChange.append(1/qs[i]*state[i+1])
        # recruitment of uncom's by option i+1
        probsChange.append(l*state[0]*state[i+1]/N)
        # cross-inhibition of different options to option i+1; mind that as cross_in_func is being used this prob shall not be divided by N
        for j in range(Nsites):
            if i != j:
                ci_pop_frac = state[j+1]/N
                # if len(ci_kwargs) == 0:
                #     ci_prob = lci*state[i+1]*cross_in_func(ci_pop_frac, ci_kwargs[0])    
                # if len(ci_kwargs) == 3:
                #     ci_prob = lci*state[i+1]*cross_in_func(ci_pop_frac, ci_kwargs[0])
                ci_prob = ci_pop_frac
                probsChange.append(ci_prob)
    probSum = sum(probsChange)
    # timeInterval = np.random.exponential(1/probSum)
    timeInterval = rng.exponential(1/probSum)
    if timeInterval > timeLeft:
        return True, timeLeft
    # tower sample to select the reaction:
    probsChange = [pc / probSum for pc in probsChange]
    indexSelReac = -1
    randReac = 0.0
    while (randReac == 0.0):
        # randReac = np.random.random_sample()
        randReac = rng.random()
    bottom = 0.0
    for i,prob in enumerate(probsChange):
        if (randReac >= bottom and randReac < (bottom+prob)):
            indexSelReac = i
            break
        bottom += prob
    state += np.array(vecsChange[indexSelReac])
    return False, timeInterval

@jit
def LESgillespieSim(initial_state, pis, qs, l, lci, ci_kwargs, N, maxTime, rng, save_time_evo_ts_tuple = (0.2, 1)):
    ### save_time_evo_ts_tuple = (time step when t<=10, time step when t > 10)
    state = np.array(initial_state)
    t = 0
    # Creating the list of vector of change
    vecsChange = []
    for i in range(1,Nsites+1):
        # possible transitions: discovery, abandonment, recruitment, cross-inhibition
        for j in range(3+Nsites-1): # disc, aband, recruit, and Nsites cross inhs
            vec_change = [0]*(Nsites+1)
            if j==0 or j==2: # discovery, recruitment
                vec_change[0], vec_change[i] = -1, +1
            # if j==1 or j==3: # abandoment, cross-inhibition
            else:
                vec_change[0], vec_change[i] = +1, -1
            vecsChange.append(vec_change)
    # save time evo:
    time_evo = [[0.0],]
    aux = [[state[i]/N, ] for i in range(Nsites+1)]
    time_evo.extend(aux)
    t_since_last_save_ts = 0.0
    ######################## START SIMULATION LOOP ########################
    while t < maxTime:
        # prevState = copy.deepcopy(state)
        simFinished, timeStep = LESgillespieStep(state, pis, qs, l, lci, ci_kwargs, N, vecsChange, maxTime-t, rng)
        t += timeStep
        # Save whole time evolution:
        if t >= 10:
            save_time_evo_ts = save_time_evo_ts_tuple[1]
        else:
            save_time_evo_ts = save_time_evo_ts_tuple[0]
        t_since_last_save_ts = t_since_last_save_ts + timeStep
        if t_since_last_save_ts > save_time_evo_ts:
            time_evo[0].append(t)
            for i in range(1,Nsites+2):
                time_evo[i].append(state[i-1]/N)
            t_since_last_save_ts = 0.0
        if simFinished:
            break
    ######################## FINISH SIMULATION LOOP ########################
    # before converting values to average, save them for the SS distribution, if required:
    return state, time_evo

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-l', help='lambda', type=float)
    parser.add_argument('-lci', help='lambda ci', type=float)
    parser.add_argument('-ci_kwargs', help='(cimode; ci_x0, ci_a)', type=lambda s: [float(item) for item in s.split(',')], default=[0, 0, 0])
    parser.add_argument('-N', type=int, help='Number of agents')
    parser.add_argument('-maxTime', type=float, help='simulation time')
    parser.add_argument('-Nrea', type=int, help='Number of realizations')
    parser.add_argument('-ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    # boolean arguments 
    parser.add_argument('--final_state', type=bool, help='Print each realization final state', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    pis, qs, l, lci, ci_kwargs, N, maxTime, Nrea, ic = args.pis, args.qs, args.l, args.lci, args.ci_kwargs, args.N, args.maxTime, args.Nrea, args.ic
    printFinalState = args.final_state
    # ci_kwargs = ['sigmoid1', 0.5, 50 ]
    # ci_kwargs = ['lin', ]
    ci_kwargs[0] = int(ci_kwargs[0])
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
    # fsavg = [0.0]*(Nsites+1)
    pichain = '_'.join([str(pi) for pi in pis])
    qchain = '_'.join([str(q) for q in qs])
    ci_kwargs_chain = '_'.join([str(cikw) for cikw in ci_kwargs])
    evosFolder = f'sim_results_evos_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}_N_{N}_ic_{ic}'
    call(f'mkdir -p {evosFolder}/', shell=True)
    ##### START REALIZATIONS LOOP #####
    for i in range(Nrea):
        finalState, time_evo = LESgillespieSim(bots_per_site, pis, qs, l, lci, ci_kwargs, N, maxTime, rng, save_time_evo_ts_tuple = (0.2, 1))
        dfevo = pd.DataFrame({'time':time_evo[0]})
        for j in range(1,Nsites+2):
            dfevo[f'f{j-1}'] = time_evo[j]
        dfevo.to_csv(f'{evosFolder}/time_evo_rea_{i}.csv', index=False)
        if printFinalState:
            finalStatefs = [s/N for s in finalState]
            print(f'Final State: {finalStatefs}')
    ##### END REALIZATIONS LOOP #####
    
    call(f'tar -czf {evosFolder}.tar.gz {evosFolder}', shell=True)
    call(f'rm -r {evosFolder}', shell=True)