# The intention is to make a program capable of getting the stationary state from numerical integration and saving to a dataframe
# for the moment I'm making a df for each number of sites!
# HOW TO USE THIS SCRIPT: essentially, iterates over many lambdas;
# It recieves one set of (pi1, pi2, ...) and (q1, q2, ...) + the number of agents N and the initical condition ic
# It also recieves two values of lambda and the lambda step
# resulting dataframe columns:
# pi1,pi2,...,q1,q2,...,l,f1,f2,...,ic
import pandas as pd
import numpy as np
import argparse
import os
import sys
sys.path.append('../')
from package_global_functions import *
# why use Popen, PIPE: https://stackoverflow.com/questions/1996518/retrieving-the-output-of-subprocess-call
from subprocess import Popen, PIPE, call
from more_sites import prepare_ic

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/more_sites/results'
    if not os.path.exists(path):
        call(f'mkdir -p {path}', shell=True)
else:
    path = '/results'

def intEvo_iter_l(pis, qs, ls, dl, Nsites, ic):
    resFile = f'results_int_Nsites_{Nsites}.csv'
    all_ls = np.arange(ls[0], round(ls[1]+dl, len(str(dl).split('.')[-1])), dl)
    all_ls = np.around(all_ls, len(str(dl).split('.')[-1]))
    fs_l_evo = [[] for _ in range(Nsites+1)]
    for l in all_ls:
        callstr = 'python get_deterministic_solutions.py '
        callstr += f"-pis {','.join([str(pi) for pi in pis])} -qs {','.join([str(q) for q in qs])} {l} {ic}"
        p = Popen(callstr, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        fs = [float(o) for o in output.split(b' ')]
        for i in range(Nsites+1):
            fs_l_evo[i].append(fs[i])
    results, N_stored_results = {}, len(all_ls)
    for i in range(1,Nsites+1):
        results[f'pi{i}'] = [pis[i-1]]*N_stored_results
    for i in range(1,Nsites+1):
        results[f'q{i}'] = [qs[i-1]]*N_stored_results
    results['l'] = list(all_ls)
    for i in range(Nsites+1):
        results[f'f{i}'] = fs_l_evo[i]
    results['ic'] = [ic]*N_stored_results
    df_new = pd.DataFrame(results)
    if os.path.exists(path + '/' + resFile):
        df_old = pd.read_csv(path + '/' + resFile)
        for index,row in df_new.iterrows():   
            bool_series = (df_old['l']==row['l']) & (df_old['ic'] == row['ic'])
            for i in range(1,Nsites+1):
                bool_series = bool_series & (df_old[f'pi{i}']==row[f'pi{i}']) & (df_old[f'q{i}']==row[f'q{i}'])
            if not(df_old.loc[bool_series].empty):
                df_old.drop(df_old.loc[bool_series].index,inplace=True)
        # append the new results to the csv dataframe
        df_old = pd.concat([df_old,df_new],ignore_index=True)
        df_old = df_old.sort_values(by=[f'q{Nsites}', f'pi{Nsites}','l'], ignore_index=True)
        df_old.to_csv(path + '/' + resFile, index=False)
    else:
        df_new.to_csv(path + '/' + resFile, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-ls', help='lambdas, separated by commas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('dl', help='lambda step', type=float)
    parser.add_argument('ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    args = parser.parse_args()
    pis, qs, ls, dl, ic, = args.pis, args.qs, args.ls, args.dl, args.ic
    if len(pis) != len(qs):
        print('Input number of pis different from qualities. Aborting.')
        exit()
    Nsites = len(pis)
    intEvo_iter_l(pis, qs, ls, dl, Nsites, ic)
