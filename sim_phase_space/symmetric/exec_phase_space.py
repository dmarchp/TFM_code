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

seed(datetime.now().timestamp())

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/sim_phase_space/symmetric/results'
else:
    print('CAREFUL! NO EXTERNAL SSD!')
    path = './results'

parser = argparse.ArgumentParser()
parser.add_argument('q1', type=float, help='site 1 quality')
parser.add_argument('q2', type=float, help='site 2 quality')
parser.add_argument('N', type=int, help='Number of bots to simulate')
parser.add_argument('maxTime', type=int, help='Simulation time; the script stationary_results.py computes from 1000 onwards, keep in mind...')
parser.add_argument('--ic', type=str, help='Initial condition: (no (all uncomitted), pi, pi hard) -> (N/P/Phard)', default='N')
parser.add_argument('--num_rea', type=int, help='Number of realizations, default 50', default=50)
parser.add_argument('--pi_lims', type=float, help='pi limits, defalt (0.0, 0.5)', nargs='+', default=[0.0, 0.5])
parser.add_argument('--dpi', type=float, help='delta pi, default 0.05', default=0.05)
parser.add_argument('--l_lims', type=float, help='lambda limits, default (0.0, 1.0)', nargs='+', default=[0.0, 1.0])
parser.add_argument('--dl', type=float, help='delta lambda, default 0.05', default=0.05)
args = parser.parse_args()

Nsites = 2
model = "Galla"

q1, q2, ic, N, maxTime = args.q1, args.q2, args.ic, args.N, args.maxTime
num_rea = args.num_rea
pi_lims, dpi, l_lims, dl =  args.pi_lims, args.dpi, args.l_lims, args.dl

# which initial condition?
if ic in ["N", "n", "uncomitted"]:
    ic = "N"
elif ic in ["P", "p", "pi"]:
    ic = "P"
elif ic in ["Phard", "phard", "p hard", "P hard", "Pi hard", "pi hard"]:
    ic = "Phard"
else:
    print("Incorrect initial condition, shuting down!")
    exit()

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

change_sim_input(froute, fin_file, qs=(q1, q2), max_time=maxTime, N_sites=Nsites, N_bots=N, ic=ic)
bots_per_site_usual = [N, 0, 0]
bots_per_site_pi0_l1 = [0, N/2, N/2]

# if hostName == 'depaula.upc.es':
#     subprocess.call(f"sed -i'' -e '30s/.*/q(:) = {q1} {q2}/' "+froute2+fin_file, shell=True)
#     subprocess.call(f"sed -i'' -e 's/^N_bots = .*/N_bots = {N}/' "+froute2+fin_file, shell=True)
#     subprocess.call(f"sed -i'' -e 's/^bots_per_site = .*/bots_per_site = {N} 0 0/' "+froute2+fin_file, shell=True)
#     ic_call = f"sed -i'' -e '34s/.*/random_bots_per_site = \"{ic}\"/' "+froute2+fin_file
#     subprocess.call(ic_call, shell=True)
# else:
#     subprocess.call(f"sed -i '30s/.*/q(:) = {q1} {q2}/' "+froute2+fin_file, shell=True)
#     subprocess.call(f"sed -i 's/^N_bots = .*/N_bots = {N}/' "+froute2+fin_file, shell=True)
#     subprocess.call(f"sed -i 's/^bots_per_site = .*/bots_per_site = {N} 0 0/' "+froute2+fin_file, shell=True)
#     ic_call = f"sed -i '34s/.*/random_bots_per_site = \"{ic}\"/' "+froute2+fin_file
#     subprocess.call(ic_call, shell=True)
    
# if both the fortran code and the initial condition are changed properly, compile the fortran code and carry on with the simulations
os.chdir(froute)
subprocess.call('make clean', shell=True)
subprocess.call('make', shell=True)
os.chdir(wd)

print("Simulating pi-sym phase space with the following parameters: ")
print(f"Site 1 quality: {q1}")
print(f"Site 2 quality: {q2}")
print(f"Model: {model}")
print(f"Initial conditions: {ic}")

# NEW WAY: SAVING TO A MESH !!
of_name = f'q1_{q1}_q2_{q2}_phase_space_{model}_ic_{ic}_Nbots_{N}.npz'

Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
Nls = int((l_lims[1] - l_lims[0])/dl) + 1
xgrid_pi, ygrid_l = np.mgrid[pi_lims[0]:pi_lims[1]:complex(0,Npis), l_lims[0]:l_lims[1]:complex(0,Nls)]
xgrid_pi, ygrid_l = np.around(xgrid_pi,2), np.around(ygrid_l,2)
grid_fs = np.empty([8, Npis, Nls])

for i,pi in enumerate(xgrid_pi[:,0]):
    for j,l in enumerate(ygrid_l[0,:]):
        if pi == 0.0 or l == 1.0:
            change_sim_input(froute, fin_file, pis=(pi, pi), lamb=l, bots_per_site=bots_per_site_pi0_l1, ic='N')
        else:
            change_sim_input(froute, fin_file, pis=(pi, pi), lamb=l, bots_per_site=bots_per_site_usual, ic=ic)
        # Change to the Fortran code directory and execute
        os.chdir(froute)
        subprocess.call("./"+fex_file+f" {randint(0,100000000)} {num_rea}", shell=True)
        os.chdir(wd)
        # Get the average values from the execution:
        df = pd.read_csv(froute+'stationary_results.csv')
        grid_fs[:,i,j] = [df['f0'].iloc[0], df['f1'].iloc[0], df['f2'].iloc[0], df['sdf0'].iloc[0], df['sdf1'].iloc[0], df['sdf2'].iloc[0], df['Q'].iloc[0], df['sdQ'].iloc[0]]


np.savez(f'{path}/{of_name}', x=xgrid_pi, y=ygrid_l, fs=grid_fs)

# subprocess.call(f"mkdir -p results/", shell=True)
# subprocess.call(f"mv {of_name} results/", shell=True)

















# which model? change accordingly the fortran code
#if model in ["G", "Galla", "galla"]:
#    subprocess.call("sed -i '65s/.*/            call update_system_galla()/' "+froute+f_file, shell=True)
#    subprocess.call("sed -i '66s/.*/            !call update_system()/' "+froute+f_file, shell=True)
#    model = "Galla"
#elif model in ["L", "List", "list"]:
#    subprocess.call("sed -i '65s/.*/            !call update_system_galla()/' "+froute+f_file, shell=True)
#    subprocess.call("sed -i '66s/.*/            call update_system()/' "+froute+f_file, shell=True)
#    model = "List"
#else:
#    print("Incorrect model introduced, shuting down!")
#    exit()
# Naaaa, simulate always galla