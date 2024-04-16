import numpy as np
from datetime import datetime
import argparse
import copy
import sys
sys.path.append('../')
from package_global_functions import *
# from more_sites import prepare_ic

# mentres faig proves
import matplotlib.pyplot as plt


def cross_in_func(pop,*kwargs):
    if not kwargs or kwargs[0] == 1 or kwargs[0] == 'lin':
        return pop
    elif kwargs[0] == 2 or kwargs[0] == 'sigmoid1':
        x0, a = kwargs[1], kwargs[2]
        return 1/(1+np.exp(-a*(pop-x0)))
    elif kwargs[0] == 3 or kwargs[0] == 'sigmoid2':
        x0, a = kwargs[1], kwargs[2]
        return 2*pop/(1+np.exp(-a*(pop-x0)))

def LESgillespieStep(state, vectorsOfChange, timeLeft):
    probabilitiesOfChange = []
    for i in range(Nsites):
        # disocvery of option i+1:
        probabilitiesOfChange.append((1-l)*pis[i]*state[0])
        # abandonment of option i+1:
        probabilitiesOfChange.append(1/qs[i]*state[i+1])
        # recruitment of uncom's by option i+1
        probabilitiesOfChange.append(l*state[0]*state[i+1]/(N-1))
        # cross-inhibition of different options to option i+1
        for j in range(Nsites):
            if i != j:
                probabilitiesOfChange.append(lci*state[i+1]*cross_in_func(state[j+1], *ci_kwargs)/(N-1))
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
    state += np.array(vectorsOfChange[indexSelReac])
    return False, timeInterval


def LESgillespieSim(initial_state,save_time_evo=False):
    # global Nsites
    state = np.array(initial_state)
    t = 0
    # Creating the list of vector of change
    vectorsOfChange = []
    for i in range(1,Nsites+1):
        # possible transitions: discovery, abandonment, recruitment, cross-inhibition
        for j in range(4):
            vec_change = [0]*(Nsites+1)
            if j==0 or j==2: # discovery, abandonment
                vec_change[0], vec_change[i] = -1, +1
            if j==1 or j==3: # abandoment, cross-inhibition
                vec_change[0], vec_change[i] = +1, -1
            vectorsOfChange.append(vec_change)
    if save_time_evo:
        time_evo = [[0.0],]
        aux = [[state[i]/N, ] for i in range(Nsites+1)]
        time_evo.extend(aux)
    while t < maxTime:
        # prevState = copy.deepcopy(state)
        simFinished, timeStep = LESgillespieStep(state, vectorsOfChange, maxTime-t)
        t += timeStep
        if save_time_evo:
            time_evo[0].append(t)
            for i in range(1,Nsites+2):
                time_evo[i].append(state[i-1]/N)
        if simFinished:
            break
    if save_time_evo:
        dfevo = pd.DataFrame({'time':time_evo[0]})
        for i in range(1,Nsites+2):
            dfevo[f'f{i-1}'] = time_evo[i]
        return state, dfevo
    else:
        return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-l', help='lambda', type=float)
    parser.add_argument('-lci', help='lambda ci', type=float)
    parser.add_argument('-N', type=int, help='Number of agents')
    parser.add_argument('-maxTime', type=float, help='simulation time')
    parser.add_argument('-Nrea', type=int, help='Number of realizations')
    parser.add_argument('-ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    args = parser.parse_args()
    pis, qs, l, lci, N, maxTime, Nrea, ic = args.pis, args.qs, args.l, args.lci, args.N, args.maxTime, args.Nrea, args.ic
    ci_kwargs = ['sigmoid1', 0.5, 50 ]
    if len(pis) != len(qs):
        print('Input number of pis different from qualities. Aborting.')
        exit()
    Nsites = len(pis)
    # assing the initial condition
    bots_per_site = prepare_ic(N, Nsites, ic)
    # initiate random number generator
    # old way; should not be used:
    # rnd_seed = int(datetime.now().timestamp())
    # np.random.seed(rnd_seed)
    # better instead used this: this generator is globaly seen by the gillespie step function (is passed as an argument to the gillespie step function)
    rng = np.random.default_rng(seed=int(datetime.now().timestamp()))
    # run gillespie
    # fsavg = [0.0]*(Nsites+1)
    fsavg_rea = [[] for i in range(Nsites+1)]
    for i in range(Nrea):
        # print(f'Simulation {i}, initial state: ', bots_per_site)
        # finalState = LESgillespieSim(bots_per_site)
        finalState, dfevo = LESgillespieSim(bots_per_site, save_time_evo=True)
        finalStatefs = [s/N for s in finalState]
        # print(f'Simulation {i}, final state:', finalStatefs)
        # for j in range(Nsites+1):
            # fsavg[j] += finalStatefs[j]
        # plot time evos:
        fig, ax = plt.subplots(1,1,constrained_layout=True)
        ax.set(xlabel='time', ylabel=r'$f_j$')
        ax.plot(dfevo['time'], dfevo['f0'], color='r')
        ax.plot(dfevo['time'], dfevo['f1'], color='g')
        ax.plot(dfevo['time'], dfevo['f2'], color='b')
        fig.savefig(f'time_evo_rea_{i}.png')
        dfevo.to_csv(f'time_evo_rea_{i}.csv', index=False)
        # compute averages with last 20% of timesteps
        timeForAvg = maxTime - 0.2*maxTime
        dfevo = dfevo.query('time >= @timeForAvg')
        for j in range(Nsites+1):
            fsavg_rea[j].append(np.average(dfevo[f'f{j}']))
    # average only over the final step:
    # fsavg = [fsum/Nrea for fsum in fsavg]
    # print(f'Final averages over {Nrea} simulations: ', fsavg)
    # (averages, std error) over the final 20% of the time evolution:
    fsavg2 = np.array([(np.average(fsavg_rea[i]), np.std(fsavg_rea[i])) for i in range(Nsites+1)])
    print(f'Final averages: ', fsavg2[:,0])
    

