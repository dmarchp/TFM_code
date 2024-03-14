import os
import glob
from subprocess import call
from random import seed, randint
import numpy as np
import pandas as pd
import argparse
from datetime import datetime
import random
import sys
sys.path.append('../')
from package_global_functions import *

Nsites = 2
Nrea = 100
max_time = 2500


extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/evo_to_stationary_frozen/time_evos_dif_cond'
else:
    path = '/time_evos_dif_cond'

# input to Fortran code route:
if getPCname() == 'depaula.upc.es':
    froute = '/Users/david/Desktop/Uni_code/TFM_code/frozen_positions_new/'
else:
    froute = "/home/david/Desktop/Uni_code/TFM_code/frozen_positions_new/"
fin_file = 'input_template_fp.txt'
fex_file = 'main.x'
f_file = 'main_fp.f90'


# SIMULATION FUNCTION - Uses the fortran code in "frozen_positions":
def simEvo_frozen(pi1, pi2, q1, q2, l, N, ic, bots_per_site, arena_r, interac_r, exclusion_r, push):
    random.seed(datetime.now().timestamp())
    pushLabel = "push" if push == ".true." else "nopush"
    if ic=='N':
        newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}_{pushLabel}'
        newFolderName_indv_st = f'time_evo_indv_states_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}_{pushLabel}'
    elif ic=='T':
        newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_thirds_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}_{pushLabel}'
        newFolderName_indv_st = f'time_evo_indv_states_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_thirds_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}_{pushLabel}'
    elif ic=='J':
        newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_julia_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}_{pushLabel}'
        newFolderName_indv_st = f'time_evo_indv_states_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_julia_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}_{pushLabel}'
    if os.path.exists(f'{path}/{newFolderName}'):
        Nfiles = len(glob.glob(f'{path}/{newFolderName}/*'))
        if Nfiles == Nrea:
            print(f'There are already {Nrea} trajectories with these parameters.')
            #return
    # Working directory and simulation execution files  
    wd = os.getcwd()
    change_sim_input(froute, fin_file, pis=(pi1, pi2), qs=(q1, q2), lamb=l, max_time=max_time, N_sites=Nsites, N_bots=N, 
                     bots_per_site=bots_per_site, arena_r=arena_r, interac_r=interac_r, exclusion_r=exclusion_r, push=push)
    # Execute simulations:
    os.chdir(froute)
    call("./"+fex_file+f" {randint(0,100000000)} {Nrea}", shell=True)
    os.chdir(wd)
    # Save the time evolutions:
    call(f'tar -xzf {froute}time_evo_csv.tar.gz', shell=True)
    call(f'mv time_evo_csv/ {newFolderName}', shell=True)
    call(f'mkdir -p {path}', shell=True)
    if os.path.exists(f'{path}/{newFolderName}'):
        call(f'rm -r {path}/{newFolderName}', shell=True)
    call(f'mv {newFolderName} {path}', shell=True)
    # save the time evolutions of the individual states:
    call(f'tar -xzf {froute}time_evo_indv_states.tar.gz', shell=True)
    call(f'mv time_evo_indv_states/ {newFolderName_indv_st}', shell=True)
    call(f'mkdir -p {path}', shell=True)
    if os.path.exists(f'{path}/{newFolderName_indv_st}'):
        call(f'rm -r {path}/{newFolderName_indv_st}', shell=True)
    call(f'mv {newFolderName_indv_st} {path}', shell=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pi1', type=float, help='site 1 prob')
    parser.add_argument('pi2', type=float, help='site 2 prob')
    parser.add_argument('q1', type=float, help='site 1 quality')
    parser.add_argument('q2', type=float, help='site 2 quality')
    parser.add_argument('l', type=float, help='interdependence (lambda)')
    parser.add_argument('N', type=int, help='Number of agents')
    parser.add_argument('ic', type=str, help="Initial conditions. N for all uncomitted, T for 1/3 each, J for Julia's ic's (0.14, 0.43, 0.43)")
    parser.add_argument('arena_r', type=float, help="Radius of the arena")
    parser.add_argument('interac_r', type=float, help="Radius of interaction")
    parser.add_argument('exclusion_r', type=float, help="Radius of exclusion")
    parser.add_argument('push', type=int, help='Push or no push (1/0)')
    args = parser.parse_args()
    pi1, pi2, q1, q2, l, N, ic = args.pi1, args.pi2, args.q1, args.q2, args.l, args.N, args.ic
    arena_r, interac_r, exclusion_r = args.arena_r, args.interac_r, args.exclusion_r
    if args.push:
        push = ".true."
    else:
        push = ".false."
    # INITIAL CONDITIONS:
    if ic=='N':
        bots_per_site = [N, 0, 0]
    elif ic=='T':
        base_value = int(N/3)
        bots_per_site = [base_value]*3
        if (N - 3*base_value) == 1:
            bots_per_site[0] += 1
        elif (N - 3*base_value) == 2:
            bots_per_site[1] += 1
            bots_per_site[2] += 1
        else:
            print('REVISE WHAT YOU ARE DOING WITH THE INITIAL CONDITONS!!')
            exit()
    elif ic=='J':
        bots_per_site = [round(0.14*N), round(0.43*N), round(0.43*N)] # probably int() is not necessary
        if (N - sum(bots_per_site)):
            print('REVISE WHAT YOU ARE DOING WITH THE INITIAL CONDITONS!!')
            exit()
    simEvo_frozen(pi1, pi2, q1, q2, l, N, ic, bots_per_site, arena_r, interac_r, exclusion_r, push)

if __name__ == '__main__':
    main()