import os
import glob
from subprocess import call
from random import seed, randint
import numpy as np
import pandas as pd
import argparse
import sys
sys.path.append('../')
from package_global_functions import *

parser = argparse.ArgumentParser()
parser.add_argument('pi1', type=float, help='site 1 prob')
parser.add_argument('pi2', type=float, help='site 2 prob')
parser.add_argument('q1', type=int, help='site 1 quality')
parser.add_argument('q2', type=int, help='site 2 quality')
parser.add_argument('l', type=float, help='interdependence (lambda)')
parser.add_argument('N', type=int, help='Number of agents')
parser.add_argument('ic', type=str, help="Initial conditions. N for all uncomitted, T for 1/3 each, J for Julia's ic's (0.14, 0.43, 0.43)")
parser.add_argument('inSeed', type=int, help='seed')

args = parser.parse_args()

pi1, pi2, q1, q2, l, N, ic, inSeed = args.pi1, args.pi2, args.q1, args.q2, args.l, args.N, args.ic, args.inSeed

# q1, q2 = 7, 10
# pi1, pi2 = 0.1, 0.1
# l = 0.6
# N = 500
Nsites = 2
# inSeed = 21321
seed(inSeed)

Nrea = 10
max_time = 2000

if ic=='N':
    newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
elif ic=='T':
    newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_thirds'
elif ic=='J':
    newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_julia'

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/evo_to_stationary/time_evos_dif_cond'
else:
    path = '/time_evos_dif_cond'

if os.path.exists(f'{path}/{newFolderName}'):
    Nfiles = len(glob.glob(f'{path}/{newFolderName}/*'))
    if Nfiles == Nrea:
        print(f'There are already {Nrea} trajectories with these parameters.')
        exit()

# Working directory and simulation execution files  
wd = os.getcwd()
# input to Fortran code route:
froute = "/home/david/Desktop/Uni_code/TFM_code/clean_version/"
fin_file = 'input_template.txt'
fex_file = 'main.x'
f_file = 'main.f90'

call(f"sed -i '14s/.*/max_time = {max_time}/' "+froute+fin_file, shell=True)
call(f"sed -i '17s/.*/lambda = {l}/' "+froute+fin_file, shell=True)
call(f"sed -i '27s/.*/pi(:) = {pi1} {pi2}/' "+froute+fin_file, shell=True)
call(f"sed -i '30s/.*/q(:) = {q1} {q2}/' "+froute+fin_file, shell=True)
call(f"sed -i '13s/.*/N_sites = {Nsites}/' "+froute+fin_file, shell=True)
call(f"sed -i '12s/.*/N_bots = {N}/' "+froute+fin_file, shell=True)

# INITIAL CONDITIONS:
if ic=='N':
    bots_per_site = [N, 0, 0]
    # zero_sites_str = ''
    # for i in range(Nsites):
    #     zero_sites_str += '0 '
    # call(f"sed -i '35s/.*/bots_per_site = {N} "+zero_sites_str+"/' "+froute+fin_file, shell=True)
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
call(f"sed -i '35s/.*/bots_per_site = {bots_per_site[0]} {bots_per_site[1]} {bots_per_site[2]} /' "+froute+fin_file, shell=True)
        

# Execute simulations:
os.chdir(froute)
call("./"+fex_file+f" {randint(0,100000000)} {Nrea}", shell=True)
os.chdir(wd)

# Save the time evolutions:
call(f'tar -xzf {froute}time_evo_csv.tar.gz', shell=True)
call(f'mv time_evo_csv {newFolderName}', shell=True)
call(f'mkdir -p {path}', shell=True)
if os.path.exists(f'{path}/{newFolderName}'):
    call(f'rm -r {path}/{newFolderName}', shell=True)
call(f'mv {newFolderName} {path}', shell=True)


# Make the Euler integration:
if ic=='N':
    intEvoName = path + f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_Euler.csv'
elif ic=='T':
    intEvoName = path + f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_thirds_Euler.csv'
elif ic=='J':
    intEvoName = path + f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ic_julia_Euler.csv'

def fs_evo_eq(fs,pi1,pi2,q1,q2,l):
    df1dt = fs[0]*((1-l)*pi1+l*fs[1]) - fs[1]/q1
    df2dt = fs[0]*((1-l)*pi2+l*fs[2]) - fs[2]/q2
    return df1dt, df2dt

if not os.path.exists(intEvoName):
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