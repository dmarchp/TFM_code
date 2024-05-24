import numpy as np
from datetime import datetime
import argparse
import sys
import os
from subprocess import call
sys.path.append('../')
from package_global_functions import *
import matplotlib.pyplot as plt

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    resPath = extSSDpath + getProjectFoldername() + '/gillespie_sim_ci_Reina/results'
else:
    resPath = '/results'

if not os.path.exists(resPath):
    call(f'mkdir -p {resPath}', shell=True)

def cross_in_func(pop,*kwargs):
    ### kwargs ###
    # first: linear, sigmoid 1 or 2...
    # second: x0
    # third: a
    # fouth: make superior part of the sigmoid linear (True) or not
    if not kwargs or kwargs[0] == 0 or kwargs[0] == 'lin':
        return pop
    elif kwargs[0] == 1 or kwargs[0] == 'sigmoid1':
        x0, a = kwargs[1], kwargs[2]
        cival = 1/(1+np.exp(-a*(pop-x0))) 
        if len(kwargs) == 4 and kwargs[3]:
            cival = min(cival, pop)
        return cival
    elif kwargs[0] == 2 or kwargs[0] == 'sigmoid2':
        x0, a = kwargs[1], kwargs[2]
        return pop/(1+np.exp(-a*(pop-x0)))

def REINAgillespieStep(state, vectorsOfChange, timeLeft):
    probabilitiesOfChange = [] # follow same order as vectorsOfChange, i.e. recruitment, cross-inh's, noise1 "discovery", noise1 "abandonment", noise2 "switching"
    for i in range(Nsites):
        # recruitment of uncom's by option i+1
        probabilitiesOfChange.append(qs[i]*state[0]*state[i+1]/N)
        # cross-inhibition of different options to option i+1; mind that as cross_in_func is being used this prob shall not be divided by N 
        for j in range(Nsites):
            if i != j:
                # probabilitiesOfChange.append(lci*state[i+1]*cross_in_func(state[j+1], *ci_kwargs)/(N-1))
                # probabilitiesOfChange.append(state[i+1]*qs[j]*cross_in_func(state[j+1]/N, *ci_kwargs))
                # what if cross inhibition is not quality modulated
                if ci_indep_q:
                    probabilitiesOfChange.append(state[i+1]*cross_in_func(state[j+1]/N, *ci_kwargs))
                else:
                    probabilitiesOfChange.append(state[i+1]*qs[j]*cross_in_func(state[j+1]/N, *ci_kwargs))
        # noise type 1 discovery
        probabilitiesOfChange.append(state[0]*noise1)
        # noise type 1 abandonment
        probabilitiesOfChange.append(state[i+1]*noise1)
        # noise type 2 switching
        probabilitiesOfChange.append(state[i+1]*noise2)
    probSum = sum(probabilitiesOfChange)
    # timeInterval = np.random.exponential(1/probSum)
    timeInterval = rng.exponential(1/probSum)
    if timeInterval > timeLeft:
        return True, timeLeft
    # tower sample to select the reaction:
    probabilitiesOfChange = [pc / probSum for pc in probabilitiesOfChange]
    indexSelReac = -1
    randReac = 0.0
    while (randReac == 0.0):
        # randReac = np.random.random_sample()
        randReac = rng.random()
    bottom = 0.0
    for i,prob in enumerate(probabilitiesOfChange):
        if (randReac >= bottom and randReac < (bottom+prob)):
            indexSelReac = i
            break
        bottom += prob
    if (indexSelReac == -1):
        print('Problem in selecting a reaction!')
    # print(state)
    # print(probabilitiesOfChange)
    # print(vectorsOfChange)
    # print(indexSelReac)
    try:
        state += np.array(vectorsOfChange[indexSelReac])
    except IndexError:
        print(indexSelReac)
        print(probabilitiesOfChange)
        print(randReac)
        print(state)
        input('enter ')
    # here I would check if the value corresponds to the one in the stationary state
    # for the moment I stop controlling a fixed time in the Sim function
    return False, timeInterval

def REINASgillespieSim(initial_state, save_time_evo=False, avg_last_perc=0.2):
    # avg_last_perc = fraction of maxTime to save data for avgs
    # global Nsites
    state = np.array(initial_state)
    t = 0
    # Creating the list of vector of change
    # possible transitions: recruitment, cross-inhibition, noise-induced (consider both types, when simulating one of the probabilities will be null)
    vectorsOfChange = []
    for i in range(1,Nsites+1):
        # transitions involving state 0 (uncommitted) and site i committed (recruitment, cross-inhibition, noise type 1)
        i_up_0_down = [0]*(Nsites+1)
        i_up_0_down[0], i_up_0_down[i] = -1, +1
        i_down_0_up = [0]*(Nsites+1)
        i_down_0_up[0], i_down_0_up[i] = +1, -1
        vectorsOfChange.append(i_up_0_down) # recruitment
        for _ in range(Nsites-1):
            vectorsOfChange.append(i_down_0_up) # cross inh from each different site
        vectorsOfChange.append(i_up_0_down) # noise induced discovery (noise type 1)
        vectorsOfChange.append(i_down_0_up) # noise induced abandonment (noise type 1)
        # transitions involving state i and j (noise type 2)
        otherSites = list(range(1,Nsites+1))
        otherSites.remove(i)
        for j in otherSites:
            i_down_j_up = [0]*(Nsites+1)
            i_down_j_up[i], i_down_j_up[j] = -1, +1 # chosing the reaction noise2*pop[i] automatically reduces i increases j by one
            vectorsOfChange.append(i_down_j_up)
    if save_time_evo:
        time_evo = [[0.0],]
        aux = [[state[i]/N, ] for i in range(Nsites+1)]
        time_evo.extend(aux)
    ######################## START SIMULATION LOOP ########################
    while t < maxTime:
        # prevState = copy.deepcopy(state)
        simFinished, timeStep = REINAgillespieStep(state, vectorsOfChange, maxTime-t)
        t += timeStep
        if t > stopTime:
            simFinished = True
        if simFinished:
            break
    ######################## FINISH SIMULATION LOOP ########################
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-noiseType', help='1 or 2 (no zealotry for the moment)', type=int)
    parser.add_argument('-noise', help='Noise strength, float', type=float)
    parser.add_argument('-ci_kwargs', help='(cimode; ci_x0, ci_a)', type=lambda s: [float(item) for item in s.split(',')], default=[0, ])
    parser.add_argument('-N', type=int, help='Number of agents')
    parser.add_argument('-maxTime', type=float, help='simulation time')
    parser.add_argument('-Nrea', type=int, help='Number of realizations')
    parser.add_argument('-ic', type=str, help="Initial conditions. specific format: e.g. p50-25-25, else use N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    # boolean arguments 
    parser.add_argument('--ci_indep_q', type=bool, help='Make cross inhibition independent of the site qualities', action=argparse.BooleanOptionalAction)
    parser.add_argument('--final_state', type=bool, help='Print each realization final state', action=argparse.BooleanOptionalAction)
    parser.add_argument('--save_win_count', type=bool, help='Save winner percentage count to csv file', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    qs, noiseType, noise, ci_kwargs, N, maxTime, Nrea, ic = args.qs, args.noiseType, args.noise, args.ci_kwargs, args.N, args.maxTime, args.Nrea, args.ic
    ci_indep_q, printFinalState, saveWC = args.ci_indep_q, args.final_state, args.save_win_count
    if ci_indep_q == None:
        ci_indep_q = False
    ci_kwargs[0] = int(ci_kwargs[0])
    Nsites = len(qs)
    #### noise parameters ####
    if noiseType == 1:
        noise1, noise2 = noise, 0.0
    elif noiseType == 2:
        noise1, noise2 = 0.0, noise
    else:
        noise1, noise2 = 0.0, 0.0 # noiseless model....
    #### assing the initial condition ####
    bots_per_site = prepare_ic(N, Nsites, ic)
    rng = np.random.default_rng(seed=int(datetime.now().timestamp()))
    #### get the numerical solution from the ODE integration ####
    ## to do; for the moment stop the simulation at a time that surely is stationary
    if ci_kwargs[0] == 0:
        if noise <= 0.15:
            stopTime = 30.0
        else:
            stopTime = 50.0
    else:
        stopTime = 20.0
    #### RUN GILLESPIE SIMULATIONS ####
    fsavg_rea = [[] for i in range(Nsites+1)]
    qchain = '_'.join([str(q) for q in qs])
    ci_kwargs_chain = '_'.join([str(cikw) for cikw in ci_kwargs])
    ##### START REALIZATIONS LOOP #####
    countsWinner = [0, 0]
    for i in range(Nrea):
        # if i%500 == 0:
        #     print(f'exec rea {i}')
        finalState = REINASgillespieSim(bots_per_site)
        if printFinalState:
            finalStatefs = [s/N for s in finalState]
            print(f'Final State: {finalStatefs}')
        if finalState[1] > finalState[2]:
            countsWinner[0] += 1
        else:
            countsWinner[1] += 1
    ##### END REALIZATIONS LOOP #####
    print(*countsWinner)

    # add result to the dataframe...
    if saveWC:
        new_row = pd.DataFrame({'q1':[qs[0], ], 'q2':[qs[1], ], 'noiseType': [noiseType], 'noise':[noise, ],
                        'ci_kwargs':[tuple(ci_kwargs), ], 'N':[N, ], 'ic':[ic, ], 'Nrea':[Nrea, ], 'ci_indep_q':[ci_indep_q, ],
                        'f1win':[countsWinner[0]/Nrea, ], 'f2win':[countsWinner[1]/Nrea, ]})
        if os.path.exists(f'{resPath}/winner_perc_data.csv'):
            df = pd.read_csv(f'{resPath}/winner_perc_data.csv')
            df = pd.concat([df, new_row], ignore_index=True)
            df = df.sort_values(by=['q1', 'q2', 'ci_kwargs', 'ci_indep_q', 'N', 'Nrea'], ignore_index=True)
            df.to_csv(f'{resPath}/winner_perc_data.csv', index=False)
        else:
            new_row.to_csv(f'{resPath}/winner_perc_data.csv', index=False)