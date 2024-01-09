import os
import glob
from subprocess import call
import numpy as np
import pandas as pd
import argparse
import sys
sys.path.append('../')
from package_global_functions import *
import random
from datetime import datetime

Nrea = 24
max_time = 5000

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/more_sites/time_evos_dif_cond'
else:
    path = '/time_evos_dif_cond'

# input to Fortran code route:
if getPCname() == 'depaula.upc.es':
    froute = '/Users/david/Desktop/Uni_code/TFM_code/clean_version/'
else:
    froute = "/home/david/Desktop/Uni_code/TFM_code/clean_version/"
fin_file = 'input_template.txt'
fex_file = 'main.x'
f_file = 'main.f90'

def prepare_ic(N, Nsites, ic):
    bots_per_site = [0]*(Nsites+1)
    if ic == 'N':
        bots_per_site[0] = N
    elif ic == 'E':
        bots_per_site[1:] = [int(N/Nsites)]*Nsites
        remaining = N%Nsites
        bots_per_site[1:1+remaining] = [b+1 for b in bots_per_site[1:1+remaining]]
    elif ic == 'E0':
        bots_per_site = [int(N/(Nsites+1))]*(Nsites+1)
        remaining = N%(Nsites+1)
        bots_per_site[0:0+remaining] = [b+1 for b in bots_per_site[0:0+remaining]]
    return bots_per_site

def simEvo(pis, qs, l, N, Nsites, ic, bots_per_site, max_time, Nrea):
    newFolderName = (f"time_evo_csv_N_{N}_Nsites_{Nsites}_pis_{'_'.join([str(pi) for pi in pis])}"
                     f"_qs_{'_'.join([str(q) for q in qs])}_l_{round(l,2)}_ic_{ic}")
    print(newFolderName)
    if os.path.exists(f'{path}/{newFolderName}'):
        Nfiles = len(glob.glob(f'{path}/{newFolderName}/*'))
        df = pd.read_csv(f'{path}/{newFolderName}/time_evo_rea_001.csv')
        lenSim = len(df['iter'])
        # if Nfiles == Nrea:
        if Nfiles == Nrea and lenSim >= max_time:
            print(f'There are already {Nrea} trajectories with these parameters and the same simulation length.')
            return
        # Working directory and simulation execution files  
    wd = os.getcwd()
    change_sim_input(froute, fin_file, pis=pis, qs=qs, lamb=l, max_time=max_time, N_sites=Nsites, N_bots=N, 
                     bots_per_site=bots_per_site)
    # Execute simulations:
    os.chdir(froute)
    call("./"+fex_file+f" {random.randint(0,100000000)} {Nrea}", shell=True)
    os.chdir(wd)
    # Save the time evolutions:
    call(f'tar -xzf {froute}time_evo_csv.tar.gz', shell=True)
    call(f'mv time_evo_csv {newFolderName}', shell=True)
    call(f'mkdir -p {path}', shell=True)
    if os.path.exists(f'{path}/{newFolderName}'):
        call(f'rm -r {path}/{newFolderName}', shell=True)
    call(f'mv {newFolderName} {path}', shell=True)

def main():
    parser = argparse.ArgumentParser()
    # https://stackoverflow.com/questions/15753701/how-can-i-pass-a-list-as-a-command-line-argument-with-argparse
    # using action append: must be handled --pis 0.1 --pis 0.2 --pis 0.3 etc...
    # parser.add_argument('--pis', action='append', type=float, required=True)
    # parser.add_argument('--qs', action='append', type=float, required=True)
    # comma separated list as argument:
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('l', type=float, help='interdependence (lambda)')
    parser.add_argument('N', type=int, help='Number of agents')
    parser.add_argument('ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    args = parser.parse_args()
    pis, qs, l, N, ic = args.pis, args.qs, args.l, args.N, args.ic
    if len(pis) != len(qs):
        print('Input number of pis different from qualities. Aborting.')
        exit()
    Nsites = len(pis)
    # assign the initial condition
    bots_per_site = prepare_ic(N, Nsites, ic)
    check = False
    # check: print parameters
    if check == True:
        print('Performing simulations with the following parameters:')
        print(f'pis: {pis}')
        print(f'qualities: {qs}')
        print(f'lambda: {l}')
        print(f'N: {N}')
        print(f'ic: {ic}, bots_per_site = {bots_per_site}')
    simEvo(pis, qs, l, N, Nsites, ic, bots_per_site, max_time, Nrea)
    

if __name__ == '__main__':
    main()