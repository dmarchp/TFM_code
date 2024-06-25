import pandas as pd
import numpy as np
import multiprocessing as mp
from subprocess import call
import sys
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    resPath = extSSDpath + getProjectFoldername() + '/gillespie_sim_ci_Reina/results'
else:
    resPath = '/results'
    print('Forgot the SSD!!!!!')

def get_win_probs(qs, noiseType, noise, ci_kwargs, N, maxTime, Nrea, ic, ci_indep_q, mpID):
    qchain_exec = ','.join([str(q) for q in qs]) 
    ci_kwargs_chainExec = ','.join([str(cikw) for cikw in ci_kwargs])
    ci_indep_q_exec = '--ci_indep_q' if ci_indep_q else ''
    print(f'getting win probs from {noiseType},{noise} {ci_kwargs}')
    call(f'python Reina_model_gill_autoStop.py  -qs {qchain_exec} -noiseType {noiseType} -noise {noise} -N {N} -maxTime {maxTime} -Nrea {Nrea} -ic {ic} -ci_kwargs {ci_kwargs_chainExec} {ci_indep_q_exec} > winprobs{mpID}.dat', shell=True)
    with open(f'winprobs{mpID}.dat', 'r') as file:
        winprobs = [float(f)/Nrea for f in file.readline().split()]
    return winprobs

paramCombs = [
    # sample line
    # [(1.0, 1.05), 1, 0.1, (2, 0.3, 500.0), 1000, 100.0, 10000, 'N', False],
]

if __name__ == '__main__':
    pool = mp.Pool(int(mp.cpu_count()/2))
    # pool = mp.Pool(1)
    res_async = [pool.apply_async(get_win_probs, args = (*paramComb, i)) for i,paramComb in enumerate(paramCombs)]
    allwinprobs = [r.get() for r in res_async]
    q1s, q2s, noiseTypes, noises, ci_kwargs_list, Ns, maxTimes, Nreas, ics, ci_indep_q_bool, winf1, winf2 = [], [], [], [], [], [], [], [], [], [], [], []
    for winprobs,paramComb in zip(allwinprobs,paramCombs):
        q1s.append(paramComb[0][0]), q2s.append(paramComb[0][1]), noiseTypes.append(paramComb[1]), noises.append(paramComb[2])
        ci_kwargs_list.append(paramComb[3]), Ns.append(paramComb[4]), maxTimes.append(paramComb[5]), Nreas.append(paramComb[6]), ics.append(paramComb[7])
        ci_indep_q_bool.append(paramComb[8]), winf1.append(winprobs[0]), winf2.append(winprobs[1])
    pool.close()
    call('rm winprobs*.dat', shell=True)
    dfwinf_new = pd.DataFrame({'q1':q1s, 'q2':q2s, 'noiseType': noiseTypes, 'noise':noises,'ci_kwargs':ci_kwargs_list, 'N':Ns, 'ic':ics, 'Nrea':Nreas,
                         'ci_indep_q':ci_indep_q_bool, 'f1win':winf1, 'f2win':winf2})
    if os.path.exists(f'{resPath}/winner_perc_data.csv'):
        dfwinf = pd.read_csv(f'{resPath}/winner_perc_data.csv')
        dfwinf = pd.concat([dfwinf, dfwinf_new], ignore_index=True)
        dfwinf = dfwinf.sort_values(by=['q1', 'q2', 'ci_kwargs', 'ci_indep_q', 'N', 'Nrea'], ignore_index=True)
        dfwinf.to_csv(f'{resPath}/winner_perc_data.csv', index=False)
    else:
        dfwinf_new = dfwinf_new.sort_values(by=['q1', 'q2', 'ci_kwargs', 'ci_indep_q', 'N', 'Nrea'], ignore_index=True)
        dfwinf_new.to_csv(f'{resPath}/winner_perc_data.csv', index=False)