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

Nsites = 2
Nrea = 5
max_time = 100000

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/evo_to_stationary/time_evos_dif_cond'
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

# SIMULATION FUNCTION - Uses the fortran code in "clean_version":
def simEvo(pi1, pi2, q1, q2, l, N, ic, bots_per_site, max_time, Nrea, lround):
    random.seed(datetime.now().timestamp())
    if ic=='N':
        newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{round(l,lround)}'
    elif ic=='T':
        newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{round(l,lround)}_ic_thirds'
    elif ic=='J':
        newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{round(l,lround)}_ic_julia'
    elif ic in ['H', '95f2', '95f1', '60f1', '60f2', '80f1', '80f2']:
        newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{round(l,lround)}_ic_{ic}'
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
    change_sim_input(froute, fin_file, pis=(pi1, pi2), qs=(q1, q2), lamb=l, max_time=max_time, N_sites=Nsites, N_bots=N, 
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


# EULER INTEGRATION FUNCTIONS:    
def fs_evo_eq(fs,pi1,pi2,q1,q2,l):
    df1dt = fs[0]*((1-l)*pi1+l*fs[1]) - fs[1]/q1
    df2dt = fs[0]*((1-l)*pi2+l*fs[2]) - fs[2]/q2
    return df1dt, df2dt

def intEvo(pi1, pi2, q1, q2, l, N, ic, bots_per_site, max_time):
    if ic=='N':
        intEvoName = path + f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_Euler.csv'
    elif ic=='T':
        intEvoName = path + f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_thirds_Euler.csv'
    elif ic=='J':
        intEvoName = path + f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_julia_Euler.csv'
    elif ic in ['H', '95f2', '95f1', '60f1','60f2', '80f1','80f2']:
        intEvoName = path + f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_{ic}_Euler.csv'
    if os.path.exists(intEvoName):
        df = pd.read_csv(intEvoName)
        max_time_done = df['iter'].iloc[-1]
    if not os.path.exists(intEvoName) or max_time > max_time_done:
        pop_fraction = np.array(bots_per_site)/N
        fs_evo = [[pop_fraction[0]],[pop_fraction[1]],[pop_fraction[2]]]
        dt = 1
        for i in range(max_time):
            df1dt, df2dt = fs_evo_eq(pop_fraction, pi1, pi2, q1, q2, l)
            dfsdt = np.array([-df1dt-df2dt, df1dt, df2dt])
            pop_fraction += dfsdt*dt
            fs_evo[0].append(pop_fraction[0]), fs_evo[1].append(pop_fraction[1]), fs_evo[2].append(pop_fraction[2])
        df = pd.DataFrame({'iter':list(range(max_time+1)), 'f0':fs_evo[0], 'f1':fs_evo[1], 'f2':fs_evo[2]})
        df.to_csv(intEvoName, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pi1', type=float, help='site 1 prob')
    parser.add_argument('pi2', type=float, help='site 2 prob')
    # parser.add_argument('q1', type=int, help='site 1 quality')
    # parser.add_argument('q2', type=int, help='site 2 quality')
    parser.add_argument('q1', type=float, help='site 1 quality')
    parser.add_argument('q2', type=float, help='site 2 quality')
    parser.add_argument('l', type=float, help='interdependence (lambda)')
    parser.add_argument('N', type=int, help='Number of agents')
    parser.add_argument('ic', type=str, help="Initial conditions. N for all uncomitted; T for 1/3 each; H for 1/2 for f1,f2; J for Julia's ic's (0.14, 0.43, 0.43), 95f[], 80f[], 60f[]")
    args = parser.parse_args()
    pi1, pi2, q1, q2, l, N, ic = args.pi1, args.pi2, args.q1, args.q2, args.l, args.N, args.ic
    lround = len(str(l).split('.')[1])
    # INITIAL CONDITIONS: better ?
    # if ic == 'julia':
    #     ...
    # elif ic == 'T':
    #     bots_per_site = prepare_ic(N, 2, 'E0')
    # elif ic == 'H':
    #     bots_per_site = prepare_ic(N, 2, 'E')
    # else:
    #     bots_per_site = prepare_ic(N, 2, ic)
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
        print(bots_per_site)
        # input('enter ')
    elif ic=='H':
        if N%2 == 0:
            bots_per_site = [0, int(N/2), int(N/2)]
        else:
            bots_per_site = [0, int(N/2), int(N/2)+1]
    # elif ic=='95f2':
    elif ic in ['95f2', '80f2', '60f2']:
        perc  = int(ic[:-2])/100
        bots_per_site = [0, int((1-perc)*N), int((perc)*N)]
        while sum(bots_per_site) != N:
            randsite = np.random.randint(1,3)
            bots_per_site[randsite] += 1
    elif ic in ['95f1', '80f1', '60f1']:
        perc  = int(ic[:-2])/100
        bots_per_site = [0, int(perc*N), int((1-perc)*N)]
        while sum(bots_per_site) != N:
            randsite = np.random.randint(1,3)
            bots_per_site[randsite] += 1
    # elif ic=='95f1':
    #     bots_per_site = [0, int(0.95*N), int(0.05*N)]
    #     while sum(bots_per_site) != N:
    #         randsite = np.random.randint(1,3)
    #         bots_per_site[randsite] += 1
    # elif ic=='60f1':
    #     bots_per_site = [0, int(0.60*N), int(0.40*N)]
    #     while sum(bots_per_site) != N:
    #         randsite = np.random.randint(1,3)
    #         bots_per_site[randsite] += 1
    elif ic=='J':
        bots_per_site = [round(0.14*N), round(0.43*N), round(0.43*N)] # probably int() is not necessary
        if (N - sum(bots_per_site)):
            print('REVISE WHAT YOU ARE DOING WITH THE INITIAL CONDITONS!!')
            exit()
        print(bots_per_site)
        # input('enter ')
    simEvo(pi1, pi2, q1, q2, l, N, ic, bots_per_site, max_time, Nrea, lround)
    intEvo(pi1, pi2, q1, q2, l, N, ic, bots_per_site, max_time)


if __name__ == '__main__':
    main()