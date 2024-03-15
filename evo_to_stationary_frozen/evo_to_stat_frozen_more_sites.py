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
from more_sites import prepare_ic

Nrea = 24
max_time = 5000

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/evo_to_stationary_frozen/time_evos_more_sites'
else:
    path = '/results'

# input to Fortran code route:
if getPCname() == 'depaula.upc.es':
    froute = '/Users/david/Desktop/Uni_code/TFM_code/frozen_positions_new/'
else:
    froute = "/home/david/Desktop/Uni_code/TFM_code/frozen_positions_new/"
fin_file = 'input_template_fp.txt'
fex_file = 'main.x'
f_file = 'main_fp.f90'


def simEvo_frozen_ms(pis, qs, l, N, ar, ir, er, push, Nsites, ic, bots_per_site, max_time, Nrea):
    pushLabel = "push" if push == ".true." else "nopush"
    pushFortran = '.true.' if push else '.false.'
    newFolderName = (f"time_evo_csv_N_{N}_Nsites_{Nsites}_pis_{'_'.join([str(pi) for pi in pis])}"
                     f"_qs_{'_'.join([str(q) for q in qs])}_l_{round(l,2)}_ar_{ar}_ir_{ir}_er_{er}_{pushLabel}_ic_{ic}")
    # individual states!! For the moment I dont keep them
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
                     bots_per_site=bots_per_site, arena_r=ar, interac_r=ir, exclusion_r=er, push=push)
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
    # random.seed(datetime.now().timestamp())
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('l', help='lambda', type=float)
    parser.add_argument('N', type=int, help='Number of agents')
    parser.add_argument('arena_r', type=float, help='arena radius')
    parser.add_argument('interac_r', type=float, help='interac radius')
    parser.add_argument('exclusion_r', type=float, help='exclusion radius')
    parser.add_argument('push', type=int, help='Push or no push (1/0)')
    parser.add_argument('ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    parser.add_argument('max_time', type=int, help='simulation time; averages are computed from the last 1000 iters from each sim')
    parser.add_argument('Nrea', type=int, help='Number of realizations')
    args = parser.parse_args()
    pis, qs, l, N, arena_r, interac_r, exclusion_r, push, ic, max_time, Nrea = args.pis, args.qs, args.l, args.N, args.arena_r, args.interac_r, args.exclusion_r, args.push, args.ic, args.max_time, args.Nrea
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
        print(f'lambda: {l}')
        print(f'N: {N}')
        print(f'arena_r: {arena_r}, interac_r: {interac_r}, exlcusion_r: {exclusion_r}')
        print(f'ic: {ic}, bots_per_site = {bots_per_site}')
    simEvo_frozen_ms(pis, qs, l , N, arena_r, interac_r, exclusion_r, push, Nsites, ic, bots_per_site, max_time, Nrea)
    

if __name__ == '__main__':
    main()