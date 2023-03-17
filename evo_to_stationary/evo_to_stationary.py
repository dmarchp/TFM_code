import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
from subprocess import call
from random import seed, randint
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
parser.add_argument('inSeed', type=int, help='seed')

args = parser.parse_args()

pi1, pi2, q1, q2, l, N, inSeed = args.pi1, args.pi2, args.q1, args.q2, args.l, args.N, args.inSeed

# q1, q2 = 7, 10
# pi1, pi2 = 0.1, 0.1
# l = 0.6
# N = 500
Nsites = 2
# inSeed = 21321
seed(inSeed)

Nrea = 10

newFolderName = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
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

call(f"sed -i '17s/.*/lambda = {l}/' "+froute+fin_file, shell=True)
call(f"sed -i '27s/.*/pi(:) = {pi1} {pi2}/' "+froute+fin_file, shell=True)
call(f"sed -i '30s/.*/q(:) = {q1} {q2}/' "+froute+fin_file, shell=True)
call(f"sed -i '13s/.*/N_sites = {Nsites}/' "+froute+fin_file, shell=True)
call(f"sed -i '12s/.*/N_bots = {N}/' "+froute+fin_file, shell=True)
zero_sites_str = ''
for i in range(Nsites):
    zero_sites_str += '0 '
call(f"sed -i '35s/.*/bots_per_site = {N} "+zero_sites_str+"/' "+froute+fin_file, shell=True)

# Execute simulations:
os.chdir(froute)
call("./"+fex_file+f" {randint(0,100000000)} {Nrea}", shell=True)
os.chdir(wd)

# Plot the time evolutions:
# fig, ax = plt.subplots()
# ax.set(xlabel='Iteration', ylabel='$f_2$', xscale='log')
# call(f'tar -xzf {froute}time_evo_csv.tar.gz', shell=True)
# for i in range(1,Nrea+1):
#     df_time_evo = pd.read_csv(f'time_evo_csv/time_evo_rea_{str(i).zfill(3)}.csv')
    # ax.plot(df_time_evo['iter'], df_time_evo['f2'])
# fig.tight_layout()
# fig.savefig(f'time_evo_f2_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.png')


# Save the time evolutions:
call(f'tar -xzf {froute}time_evo_csv.tar.gz', shell=True)
call(f'mv time_evo_csv {newFolderName}', shell=True)
call(f'mkdir -p {path}', shell=True)
if os.path.exists(f'{path}/{newFolderName}'):
    call(f'rm -r {path}/{newFolderName}', shell=True)
call(f'mv {newFolderName} {path}', shell=True)
