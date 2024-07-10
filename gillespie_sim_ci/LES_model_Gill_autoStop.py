import numpy as np
from datetime import datetime
import argparse
import copy
import sys
import os
from subprocess import call
sys.path.append('../')
from package_global_functions import *
# from more_sites import prepare_ic

# mentres faig proves
import matplotlib.pyplot as plt

# sample exec command if u feel lazy
# python LES_model_Gill_autoStop.py -pis 0.1,0.1 -qs 8.0,10.0 -l 0.1 -lci 1.0 -N 1000 -maxTime 100.0 -Nrea 10000 -ic N -ci_kwargs 2,0.3,10.0 --save_win_count

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    resPath = extSSDpath + getProjectFoldername() + '/gillespie_sim_ci/results'
else:
    resPath = '/results'




# def cross_in_func(pop,*kwargs):
#     if not kwargs or kwargs[0] == 0 or kwargs[0] == 'lin':
#         return pop
#     elif kwargs[0] == 1 or kwargs[0] == 'sigmoid1':
#         x0, a = kwargs[1], kwargs[2]
#         return 1/(1+np.exp(-a*(pop-x0)))
#     elif kwargs[0] == 2 or kwargs[0] == 'sigmoid2':
#         x0, a = kwargs[1], kwargs[2]
#         return 2*pop/(1+np.exp(-a*(pop-x0)))

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

def LESgillespieStep(state, vectorsOfChange, timeLeft):
    global f1winVal, f2winVal
    epsWinVal = 0.05
    probabilitiesOfChange = []
    for i in range(Nsites):
        # disocvery of option i+1:
        probabilitiesOfChange.append((1-l)*pis[i]*state[0])
        # abandonment of option i+1:
        probabilitiesOfChange.append(1/qs[i]*state[i+1])
        # recruitment of uncom's by option i+1
        # probabilitiesOfChange.append(l*state[0]*state[i+1]/(N-1))
        probabilitiesOfChange.append(l*state[0]*state[i+1]/N)
        # cross-inhibition of different options to option i+1; mind that as cross_in_func is being used this prob shall not be divided by N
        for j in range(Nsites):
            if i != j:
                # probabilitiesOfChange.append(lci*state[i+1]*cross_in_func(state[j+1], *ci_kwargs)/(N-1))
                probabilitiesOfChange.append(lci*state[i+1]*cross_in_func(state[j+1]/N, *ci_kwargs))
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
    # print(vectorsOfChange)
    # print(indexSelReac)
    # input('enter ')
    try:
        state += np.array(vectorsOfChange[indexSelReac])
    except IndexError:
        print(indexSelReac)
        print(probabilitiesOfChange)
        print(randReac)
        print(state)
        input('enter ')
    if abs(state[1]/N-f1winVal) < epsWinVal or abs(state[2]/N-f2winVal) < epsWinVal:
        return True, timeInterval
    else:
        return False, timeInterval


def LESgillespieSim(initial_state):
    # avg_last_perc = fraction of maxTime to save data for avgs
    # global Nsites
    state = np.array(initial_state)
    t = 0
    # Creating the list of vector of change
    vectorsOfChange = []
    for i in range(1,Nsites+1):
        # possible transitions: discovery, abandonment, recruitment, cross-inhibition
        for j in range(3+Nsites-1): # disc, aband, recruit, and Nsites cross inhs
            vec_change = [0]*(Nsites+1)
            if j==0 or j==2: # discovery, abandonment
                vec_change[0], vec_change[i] = -1, +1
            # if j==1 or j==3: # abandoment, cross-inhibition
            else:
                vec_change[0], vec_change[i] = +1, -1
            vectorsOfChange.append(vec_change)
    ######################## START SIMULATION LOOP ########################
    while t < maxTime:
        # prevState = copy.deepcopy(state)
        simFinished, timeStep = LESgillespieStep(state, vectorsOfChange, maxTime-t)
        t += timeStep
        if simFinished:
            break
    ######################## FINISH SIMULATION LOOP ########################
    # return final state, final SS average, and time evolution (if required)
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-l', help='lambda', type=float)
    parser.add_argument('-lci', help='lambda ci', type=float)
    parser.add_argument('-ci_kwargs', help='(cimode; ci_x0, ci_a)', type=lambda s: [float(item) for item in s.split(',')], default=[0, ])
    parser.add_argument('-N', type=int, help='Number of agents')
    parser.add_argument('-maxTime', type=float, help='simulation time')
    parser.add_argument('-Nrea', type=int, help='Number of realizations')
    parser.add_argument('-ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    # boolean arguments 
    parser.add_argument('--final_state', type=bool, help='Print each realization final state', action=argparse.BooleanOptionalAction)
    parser.add_argument('--save_win_count', type=bool, help='Save winner percentage count to csv file', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    pis, qs, l, lci, ci_kwargs, N, maxTime, Nrea, ic = args.pis, args.qs, args.l, args.lci, args.ci_kwargs, args.N, args.maxTime, args.Nrea, args.ic
    printFinalState, saveWC = args.final_state, args.save_win_count
    ci_kwargs[0] = int(ci_kwargs[0])
    if len(pis) != len(qs):
        print('Input number of pis different from qualities. Aborting.')
        exit()
    Nsites = len(pis)
    #### assing the initial condition ####
    bots_per_site = prepare_ic(N, Nsites, ic)
    #### initiate random number generator
    rng = np.random.default_rng(seed=int(datetime.now().timestamp()))
    #### get analytical solutions:
    pichain_exec, qchain_exec = ','.join([str(pi) for pi in pis]), ','.join([str(q) for q in qs])
    ci_kwargs_chain_exec = ','.join([str(cikw) for cikw in ci_kwargs])
    pichain = '_'.join([str(pi) for pi in pis])
    qchain = '_'.join([str(q) for q in qs])
    ci_kwargs_chain = '_'.join([str(cikw) for cikw in ci_kwargs])
    auxFname = f'sols_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_ci_kwargs_{ci_kwargs_chain}.csv'
    call(f'python ../cross_inhibition/model_sols.py -pis {pichain_exec} -qs {qchain_exec} -l {l} -lci {lci} -ci_kwargs {ci_kwargs_chain_exec} > {auxFname}', shell=True)
    colnames = ['f0', 'f1', 'f2', 'method', 'ic'] if ci_kwargs[0] != 0 else ['f0', 'f1', 'f2']
    solsdf = pd.read_csv(f'{auxFname}', names=colnames, header=None, index_col=False, sep='\s+')
    call(f'rm {auxFname}', shell=True)
    if ci_kwargs[0] != 0:
        f1winVal, f2winVal = solsdf['f1'].iloc[0], solsdf['f2'].iloc[1]
    elif ci_kwargs[0] == 0:
        if len(solsdf) == 1:
            f1winVal, f2winVal = solsdf['f1'].iloc[0], solsdf['f2'].iloc[0]
        elif len(solsdf) > 1:
            f1winVal, f2winVal = max(solsdf['f1']), max(solsdf['f2'])
    # print(solsdf)
    # print(f1winVal, f2winVal)
    # input('enter ')
    #### RUN GILLESPIE SIMULATIONS ####
    
    ##### START REALIZATIONS LOOP #####
    countsWinner = [0, 0]
    for i in range(Nrea):
        # if i%500 == 0:
        #     print(f'exec rea {i}')
        finalState = LESgillespieSim(bots_per_site)
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
        new_row = pd.DataFrame({'pi1':[pis[0], ], 'pi2':[pis[1], ], 'q1':[qs[0], ], 'q2':[qs[1], ], 'l':[l, ], 
                       'lci':[lci, ], 'ci_kwargs':[tuple(ci_kwargs), ], 'N':[N, ], 'ic':[ic, ], 'Nrea':[Nrea, ],
                        'f1win':[countsWinner[0]/Nrea, ], 'f2win':[countsWinner[1]/Nrea, ]})

        df = pd.read_csv(f'{resPath}/winner_perc_data.csv')
        df = pd.concat([df, new_row], ignore_index=True)
        df = df.sort_values(by=['pi1', 'pi2', 'q1', 'q2', 'ci_kwargs', 'l', 'lci',  'N', 'Nrea'], ignore_index=True)
        df.to_csv(f'{resPath}/winner_perc_data.csv', index=False)
    
