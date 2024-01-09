from sys import argv
import numpy as np
import argparse
import subprocess
import os
import pandas as pd
from random import seed, randint
from tqdm import tqdm
from datetime import datetime
import socket
import sys
sys.path.append('../../')
from package_global_functions import *
from more_sites import prepare_ic

seed(datetime.now().timestamp())

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/sim_phase_space/symmetric_more_sites/results'
    if not os.path.exists(path):
        subprocess.call(f'mkdir -p {path}', shell=True)
else:
    print('CAREFUL! NO EXTERNAL SSD!')
    path = './results'

parser = argparse.ArgumentParser()
parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
parser.add_argument('N', type=int, help='Number of agents')
# parser.add_argument('ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
parser.add_argument('-maxTime', type=int, help='simulation time; averages are computed from the last 1000 iters from each sim', default=11000)
parser.add_argument('-Nrea', type=int, help='Number of realizations', default=50)
parser.add_argument('-pi_lims', help='pinf,ptop; default (0.0,0.3)', type=lambda s: [float(item) for item in s.split(',')], default=[0.0,0.3])
parser.add_argument('-dpi', type=float, help='delta pi, default 0.05', default=0.05)
parser.add_argument('-l_lims', help='linf,ltop; default (0.0,1.0)', type=lambda s: [float(item) for item in s.split(',')], default=[0.0,1.0])
parser.add_argument('-dl', type=float, help='delta lambda, default 0.05', default=0.05)
args = parser.parse_args()
# qs, N, ic, max_time, Nrea = args.qs, args.N, args.ic, args.max_time, args.Nrea
qs, N, maxTime, Nrea = args.qs, args.N, args.maxTime, args.Nrea
pi_lims, dpi = args.pi_lims, args.dpi
l_lims, dl = args.l_lims, args.dl
# Initial condition is not asked; N when pi != 0, E when pi == 0.0
Nsites = len(qs)

check = True
# check: print parameters
if check == True:
    print('Executing state space map simulations with the following parameters:')
    print(f'qualities: {qs}')
    print(f'N: {N}')
    print(f'pis: from {pi_lims[0]} to {pi_lims[1]}, on {dpi} steps')
    print(f'lambda: from {l_lims[0]} to {l_lims[1]} on {dl} steps')

# working directory:
wd = os.getcwd()

# input to Fortran code route:
fin_file = 'input_template.txt'
fex_file = 'main.x'
f_file = 'main.f90'

hostName = socket.gethostname()
# input to Fortran code route:
if getPCname() == 'depaula.upc.es':
    froute = '/Users/david/Desktop/Uni_code/TFM_code/clean_version/'
else:
    froute = "/home/david/Desktop/Uni_code/TFM_code/clean_version/"

change_sim_input(froute, fin_file, qs=qs, max_time=maxTime, N_sites=Nsites, N_bots=N)

os.chdir(froute)
subprocess.call('make clean', shell=True)
subprocess.call('make', shell=True)
os.chdir(wd)

of_name = 'sym_phase_space_qs_'
for i in range(Nsites):
    of_name += f'{qs[i]}_'
of_name += f'N_{N}.npz'

Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
Nls = int((l_lims[1] - l_lims[0])/dl) + 1
xgrid_pi, ygrid_l = np.mgrid[pi_lims[0]:pi_lims[1]:complex(0,Npis), l_lims[0]:l_lims[1]:complex(0,Nls)]
xgrid_pi, ygrid_l = np.around(xgrid_pi,2), np.around(ygrid_l,2)
grid_fs = np.empty([(Nsites+1)*2+2, Npis, Nls])
#magnitudes to save in the grid:
magnitudes = []
for i in range(Nsites+1):
    magnitudes.append(f'f{i}')
for i in range(Nsites+1):
    magnitudes.append(f'sdf{i}')
magnitudes.extend(['Q', 'sdQ'])


for i,pi in enumerate(xgrid_pi[:,0]):
    for j,l in enumerate(ygrid_l[0,:]):
        if pi == 0.0 or l == 1.0:
            ic = 'E'
            bots_per_site = prepare_ic(N, Nsites, ic)
        else:
            ic = 'N'
            bots_per_site = prepare_ic(N, Nsites, ic)
        change_sim_input(froute, fin_file, pis=[pi]*Nsites, lamb=l, bots_per_site=bots_per_site, ic=ic)
        # Change to the Fortran code directory and execute
        os.chdir(froute)
        subprocess.call("./"+fex_file+f" {randint(0,100000000)} {Nrea}", shell=True)
        os.chdir(wd)
        # Get the average values from the execution:
        df = pd.read_csv(froute+'stationary_results.csv')
        for magInd in range((Nsites+1)*2+2):
            grid_fs[magInd,i,j] = df[magnitudes[magInd]].iloc[0]

np.savez(f'{path}/{of_name}', x=xgrid_pi, y=ygrid_l, fs=grid_fs)
