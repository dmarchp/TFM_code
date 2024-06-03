import pandas as pd
import numpy as np
import multiprocessing as mp
from subprocess import call
import sys
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    resPath = extSSDpath + getProjectFoldername() + '/gillespie_sim_ci/results'
else:
    resPath = '/results'
    print('Forgot the SSD!!!!!')

def get_win_probs(pis, qs, l, lci, ci_kwargs, N, maxTime, Nrea, ic, mpID):
    pichain_exec = ','.join([str(pi) for pi in pis]) 
    qchain_exec = ','.join([str(q) for q in qs]) 
    ci_kwargs_chainExec = ','.join([str(cikw) for cikw in ci_kwargs])
    print(f'getting win probs from {l}, {ci_kwargs}')
    call(f'python LES_model_Gill_autoStop.py -pis {pichain_exec} -qs {qchain_exec} -l {l} -lci {lci} -N {N} -maxTime {maxTime} -Nrea {Nrea} -ic {ic} -ci_kwargs {ci_kwargs_chainExec} > winprobs{mpID}.dat', shell=True)
    with open(f'winprobs{mpID}.dat', 'r') as file:
        winprobs = [float(f)/Nrea for f in file.readline().split()]
    return winprobs

paramCombs = [
    # sample line
    # [(0.2, 0.2), (9.0, 10.0), 0.1, 1.0, (2, 0.3, 500.0), 1000, 100.0, 10000, 'N'],

    # [(0.15, 0.15), (9.0, 10.0), 0.6, 1.0, (0, ), 1000, 100.0, 10000, 'N'],
    # [(0.15, 0.15), (9.0, 10.0), 0.6, 1.0, (1, 0.3, 10.0), 1000, 100.0, 10000, 'N'],
    # [(0.15, 0.15), (9.0, 10.0), 0.6, 1.0, (2, 0.3, 10.0), 1000, 100.0, 10000, 'N'],
    # [(0.15, 0.15), (9.0, 10.0), 0.6, 1.0, (1, 0.3, 500.0), 1000, 100.0, 10000, 'N'],
    # [(0.15, 0.15), (9.0, 10.0), 0.6, 1.0, (2, 0.3, 500.0), 1000, 100.0, 10000, 'N'],

    # [(0.25, 0.25), (9.0, 10.0), 0.6, 1.0, (0, ), 1000, 100.0, 10000, 'N'],
    # [(0.25, 0.25), (9.0, 10.0), 0.6, 1.0, (1, 0.3, 10.0), 1000, 100.0, 10000, 'N'],
    # [(0.25, 0.25), (9.0, 10.0), 0.6, 1.0, (2, 0.3, 10.0), 1000, 100.0, 10000, 'N'],
    # [(0.25, 0.25), (9.0, 10.0), 0.6, 1.0, (1, 0.3, 500.0), 1000, 100.0, 10000, 'N'],
    # [(0.25, 0.25), (9.0, 10.0), 0.6, 1.0, (2, 0.3, 500.0), 1000, 100.0, 10000, 'N'],

    [(0.1, 0.1), (9.0, 10.0), 0.1, 1.0, (1, 0.3, 20.0), 1000, 100.0, 10000, 'N'],
    [(0.1, 0.1), (9.0, 10.0), 0.15, 1.0, (1, 0.3, 20.0), 1000, 100.0, 10000, 'N'],
    [(0.1, 0.1), (9.0, 10.0), 0.2, 1.0, (1, 0.3, 20.0), 1000, 100.0, 10000, 'N'],
    [(0.1, 0.1), (9.0, 10.0), 0.3, 1.0, (1, 0.3, 20.0), 1000, 100.0, 10000, 'N'],
    [(0.1, 0.1), (9.0, 10.0), 0.45, 1.0, (1, 0.3, 20.0), 1000, 100.0, 10000, 'N'],
    [(0.1, 0.1), (9.0, 10.0), 0.6, 1.0, (1, 0.3, 20.0), 1000, 100.0, 10000, 'N'],
    [(0.1, 0.1), (9.0, 10.0), 0.75, 1.0, (1, 0.3, 20.0), 1000, 100.0, 10000, 'N'],
    [(0.1, 0.1), (9.0, 10.0), 0.9, 1.0, (1, 0.3, 20.0), 1000, 100.0, 10000, 'N'],
    
]

# this happened for pis 0.1,0.1 qs 8.0,10.0; the probabilities of f1,f2 winning are correct (at the moment the sim is stopped they are indeed winning)
# but as I want to estimate the probability of arriving at the particular fixed point, i set to 0.0,1.0 these last columns in the df
# 0.1,0.1,8.0,10.0,0.1,1.0,"(0,)",1000,N,10000,0.4622,0.5378
# 0.1,0.1,8.0,10.0,0.2,1.0,"(0,)",1000,N,10000,0.5046,0.4954
# 0.1,0.1,8.0,10.0,0.3,1.0,"(0,)",1000,N,10000,0.5014,0.4986

if __name__ == '__main__':
    pool = mp.Pool(int(mp.cpu_count()/2))
    # pool = mp.Pool(1)
    res_async = [pool.apply_async(get_win_probs, args = (*paramComb, i)) for i,paramComb in enumerate(paramCombs)]
    allwinprobs = [r.get() for r in res_async]
    pi1s, pi2s, q1s, q2s, ls, lcis, ci_kwargs_list, Ns, maxTimes, Nreas, ics, winf1, winf2 = [], [],  [], [], [], [], [], [], [], [], [], [], [],
    for winprobs,paramComb in zip(allwinprobs,paramCombs):
        pi1s.append(paramComb[0][0]), pi2s.append(paramComb[0][1]), q1s.append(paramComb[1][0]), q2s.append(paramComb[1][1])
        ls.append(paramComb[2]), lcis.append(paramComb[3]), ci_kwargs_list.append(paramComb[4]), Ns.append(paramComb[5])
        maxTimes.append(paramComb[6]), Nreas.append(paramComb[7]), ics.append(paramComb[8])
        winf1.append(winprobs[0]), winf2.append(winprobs[1])
    pool.close()
    call('rm winprobs*.dat', shell=True)
    dfwinf_new = pd.DataFrame({'pi1':pi1s, 'pi2':pi2s, 'q1':q1s, 'q2':q2s, 'l': ls, 
                       'lci':lcis, 'ci_kwargs':ci_kwargs_list, 'N':Ns, 'ic':ics, 'Nrea':Nreas,
                         'f1win':winf1, 'f2win':winf2})
    dfwinf = pd.read_csv(f'{resPath}/winner_perc_data.csv')
    dfwinf = pd.concat([dfwinf, dfwinf_new], ignore_index=True)
    dfwinf = dfwinf.sort_values(by=['pi1', 'pi2', 'q1', 'q2', 'ci_kwargs', 'l', 'lci',  'N', 'Nrea'], ignore_index=True)
    dfwinf.to_csv(f'{resPath}/winner_perc_data.csv', index=False)