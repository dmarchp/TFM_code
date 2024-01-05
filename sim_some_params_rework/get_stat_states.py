# The intention is to make a program capable of simulating for any number of sites
# and saving the stationary state to a dataframe
# for the moment I'm making a df for each number of sites!
# HOW TO USE THIS SCRIPT: essentially, simulates many lambdas; to simulate across many qs or pis make an external script...
# It recieves one set of (pi1, pi2, ...) and (q1, q2, ...) + the number of agents N and the initical condition ic
# It also recieves two values of lambda and the lambda step
# resulting dataframe columns:
# N,pi1,pi2,...,q1,q2,...,l,f1,f2,...,sdf1,sdf2,...,Q,sdQ,Nrea,simTime,ic
import pandas as pd
import numpy as np
import argparse
import os
import sys
sys.path.append('../')
from package_global_functions import *
import random
from subprocess import call
from datetime import datetime
from more_sites import prepare_ic

# make this input parameters: yes
# max_time = 1000
# Nrea = 10

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/sim_some_params_rework/results'
else:
    path = '/results'

# input to Fortran code route:
if getPCname() == 'depaula.upc.es':
    froute = '/Users/david/Desktop/Uni_code/TFM_code/clean_version/'
else:
    froute = "/home/david/Desktop/Uni_code/TFM_code/clean_version/"
fin_file = 'input_template.txt'
fex_file = 'main.x'
f_file = 'main.f90'

def simEvo_iter_lambda(pis, qs, ls, dl, Nsites, N, ic, max_time, Nrea, ow_geq_Nrea=True, ow_geq_simTime=False, ow_hard=False):
    '''
    Overwriting old results control:
    ow_geq_Nrea: if Nrea >= stored Nrea, overwrite
    ow_geq_simTime: still thinking how to define this behavior
    ow_hard: ignore this criterions and overwrite no matter what
    '''
    resFile = f'results_sim_Nsites_{Nsites}.csv'
    wd = os.getcwd()
    change_sim_input(froute, fin_file, pis=pis, qs=qs, max_time=max_time, N_sites=Nsites, N_bots=N, 
                     bots_per_site=bots_per_site)
    all_ls = np.arange(ls[0], ls[1]+dl, dl)
    all_ls = np.around(all_ls, len(str(dl).split('.')[-1]))
    # prepare the results dictionary (later df) PART1
    results = {}
    results['N'] = [N]*len(all_ls)
    for i in range(1,Nsites+1):
        results[f'pi{i}'] = [pis[i-1]]*len(all_ls)
    for i in range(1,Nsites+1):
        results[f'q{i}'] = [qs[i-1]]*len(all_ls)
    results['l'] = list(all_ls)
    for i in range(Nsites+1):
        results[f'f{i}'] = []
    for i in range(Nsites+1):
        results[f'sdf{i}'] = []
    results['Q'], results['sdQ'] = [], []
    for l in all_ls:
        change_sim_input(froute, fin_file, lamb=l)
        # Execute simulations:
        os.chdir(froute)
        call("./"+fex_file+f" {random.randint(0,100000000)} {Nrea}", shell=True)
        os.chdir(wd)
        # Get the average values from the execution:
        df = pd.read_csv(froute+'stationary_results.csv')
        for i in range(Nsites+1):
            results[f'f{i}'].append(float(df[f'f{i}'])), results[f'sdf{i}'].append(float(df[f'sdf{i}']))
        results['Q'].append(float(df['Q'])), results['sdQ'].append(float(df['sdQ']))
    # save the simulation results to the dataframe:
    results['Nrea'], results['simTime'], results['ic'] = [Nrea]*len(all_ls), [max_time]*len(all_ls), [ic]*len(all_ls)
    df_new = pd.DataFrame(results)
    call(f'mkdir -p {path}', shell=True)
    # Replace values if already present in the old df and simTime > old_simTime,  or Nrea > old_Nrea
    if os.path.exists(path + '/' + resFile):
        df_old = pd.read_csv(path + '/' + resFile)
        for index,row in df_new.iterrows():   
            bool_series = (df_old['N']==row['N']) & (df_old['l']==row['l']) & (df_old['ic'] == row['ic'])
            for i in range(1,Nsites+1):
                bool_series = bool_series & (df_old[f'pi{i}']==row[f'pi{i}']) & (df_old[f'q{i}']==row[f'q{i}'])
            if not(df_old.loc[bool_series].empty):
                # compare the number of realization and/or the length of the simulations(?)
                # if (row['Nrea'] > df_old.loc[bool_series]['Nrea']) and (row['simTime'] > df_old.loc[bool_series]['simTime']):
                if ((ow_geq_Nrea and (row['Nrea'] > df_old.loc[bool_series]['Nrea'].index)) or ow_hard):
                    df_old.drop(df_old.loc[bool_series].index,inplace=True)
        # append the new results to the csv dataframe
        df_old = pd.concat([df_old,df_new],ignore_index=True)
        df_old = df_old.sort_values(by=['N', f'q{Nsites}', f'pi{Nsites}','l'], ignore_index=True)
        df_old.to_csv(path + '/' + resFile, index=False)
    else:
        df_new.to_csv(path + '/' + resFile, index=False)





if __name__ == '__main__':
    random.seed(datetime.now().timestamp())
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-ls', help='lambdas, separated by commas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('dl', help='lambda step', type=float)
    parser.add_argument('N', type=int, help='Number of agents')
    parser.add_argument('ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    parser.add_argument('max_time', type=int, help='simulation time; averages are computed from the last 1000 iters from each sim')
    parser.add_argument('Nrea', type=int, help='Number of realizations')
    args = parser.parse_args()
    pis, qs, ls, dl, N, ic, max_time, Nrea = args.pis, args.qs, args.ls, args.dl, args.N, args.ic, args.max_time, args.Nrea
    if len(pis) != len(qs):
        print('Input number of pis different from qualities. Aborting.')
        exit()
    Nsites = len(pis)
    # assing the initial condition
    bots_per_site = prepare_ic(N, Nsites, ic)
    check = True
    # check: print parameters
    if check == True:
        print('Performing simulations with the following parameters:')
        print(f'pis: {pis}')
        print(f'qualities: {qs}')
        print(f'lambda: from {ls[0]} to {ls[1]} on {dl} steps')
        print(f'N: {N}')
        print(f'ic: {ic}, bots_per_site = {bots_per_site}')
    simEvo_iter_lambda(pis, qs, ls, dl, Nsites, N, ic, max_time, Nrea)