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
# python LES_model_gill.py -pis 0.1,0.1 -qs 9.0,10.0 -l 0.8 -lci 0.9 -N 500 -maxTime 150.0  -Nrea 10 -ic p10-0-90 -time_evo True -time_evo_plot True -ci_kwargs 1,0.35,40

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
    return False, timeInterval


def LESgillespieSim(initial_state, save_time_evo=False, avg_last_perc=0.2):
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
    if save_time_evo:
        time_evo = [[0.0],]
        aux = [[state[i]/N, ] for i in range(Nsites+1)]
        time_evo.extend(aux)
    ######################## START SIMULATION LOOP ########################
    state_ss_avg = [[], [], []]
    while t < maxTime:
        # prevState = copy.deepcopy(state)
        simFinished, timeStep = LESgillespieStep(state, vectorsOfChange, maxTime-t)
        t += timeStep
        # Save whole time evolution:
        if save_time_evo:
            time_evo[0].append(t)
            for i in range(1,Nsites+2):
                time_evo[i].append(state[i-1]/N)
        # Save values for compute stationary state averages:
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
    parser.add_argument('--ss_data', type=bool, help='Save SS values in a dataframe', action=argparse.BooleanOptionalAction)
    parser.add_argument('--time_evo', type=bool, help='Save time evolutions as df', action=argparse.BooleanOptionalAction)
    parser.add_argument('--time_evo_plot', type=bool, help='Plot time evolutions', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    pis, qs, l, lci, ci_kwargs, N, maxTime, Nrea, ic = args.pis, args.qs, args.l, args.lci, args.ci_kwargs, args.N, args.maxTime, args.Nrea, args.ic
    saveTimeEvo, plotTimeEvo, printFinalState, saveSSdata = args.time_evo, args.time_evo_plot, args.final_state, args.ss_data
    if plotTimeEvo and not saveTimeEvo:
        saveTimeEvo = True
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
    fsavg_rea = [[] for i in range(Nsites+1)]
    if saveTimeEvo:
        evosFolder = 'sim_results_evos'
        call(f'mkdir -p {evosFolder}/', shell=True)
    if saveSSdata:
        pichain = '_'.join([str(pi) for pi in pis])
        qchain = '_'.join([str(q) for q in qs])
        ci_kwargs_chain = '_'.join([str(cikw) for cikw in ci_kwargs])
        ssData_fname = f'sim_pis_{pichain}_qs_{qchain}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}_N_{N}_ic_{ic}.csv'
        ssDataPool = [[] for i in range(Nsites+1)]
    ##### START REALIZATIONS LOOP #####
    for i in range(Nrea):
        if saveTimeEvo:
            finalState, ssAvgState, dfevo = LESgillespieSim(bots_per_site, save_time_evo=True)
            dfevo.to_csv(f'{evosFolder}/time_evo_rea_{i}.csv', index=False)
        else:
            finalState, ssAvgState = LESgillespieSim(bots_per_site)
        if printFinalState:
            finalStatefs = [s/N for s in finalState]
            ssAvgStatefs = [s/N for s in ssAvgState]
            # print(*finalStatefs)
            print(f'Final State: {finalStatefs}     SS Averages: {ssAvgStatefs}')
        # print(f'Simulation {i}, final state:', finalStatefs)
        # for j in range(Nsites+1):
            # fsavg[j] += finalStatefs[j]

        #### plot time evos:
        if plotTimeEvo == True:
            if Nsites == 2:
                colors = ['xkcd:red', 'xkcd:green', 'xkcd:blue']
            if Nsites == 3:
                colors = ['xkcd:red', 'xkcd:orange', 'xkcd:green', 'xkcd:blue']
            fig, ax = plt.subplots(1,1,constrained_layout=True)
            ax.set(xlabel='time', ylabel=r'$f_j$')
            ax.plot(dfevo['time'], dfevo['f0'], color=colors[0])
            for j in range(1,Nsites+1):
                ax.plot(dfevo['time'], dfevo[f'f{j}'], color=colors[j])
            fig.savefig(f'time_evo_rea_{i}.png')
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


        
        #### compute averages with last 20% of timesteps
        # timeForAvg = maxTime - 0.2*maxTime
        # dfevo = dfevo.query('time >= @timeForAvg')
        # for j in range(Nsites+1):
        #     fsavg_rea[j].append(np.average(dfevo[f'f{j}']))

    # average only over the final step:
    # fsavg = [fsum/Nrea for fsum in fsavg]
    # print(f'Final averages over {Nrea} simulations: ', fsavg)

    #### (averages, std error) over the final 20% of the time evolution:
    # fsavg2 = np.array([(np.average(fsavg_rea[i]), np.std(fsavg_rea[i])) for i in range(Nsites+1)])
    # print(f'Final averages: ', fsavg2[:,0])
    # print(f'SEM: ', fsavg2[:,1]/np.sqrt(Nrea))
    
    if saveTimeEvo:
        call(f'tar -czf {evosFolder}.tar.gz {evosFolder}', shell=True)
        call(f'rm -r {evosFolder}', shell=True)
