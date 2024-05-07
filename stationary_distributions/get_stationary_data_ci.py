import pandas as pd
import os
from subprocess import call
from random import seed, randint
from datetime import datetime
import argparse
import sys
sys.path.append('../')
from package_global_functions import *

seed(datetime.now().timestamp())

parser = argparse.ArgumentParser()
parser.add_argument('pi1', type=float, help='site 1 prob')
parser.add_argument('pi2', type=float, help='site 2 prob')
parser.add_argument('q1', type=float, help='site 1 quality')
parser.add_argument('q2', type=float, help='site 2 quality')
parser.add_argument('l', type=float, help='interdependence (lambda)')
parser.add_argument('lci', type=float, help='ci interdep')
# parser.add_argument('cimode', type=int, help='1 for linear, 2 for sig1, 3 for sig2')
# parser.add_argument('ci_x0', type=float, help='sigmoid x0')
# parser.add_argument('ci_a', type=float, help='sigmoid a')
parser.add_argument('-ci_kwargs', help='(cimode; ci_x0, ci_a); cimode 0 for lin, 1,2 for sig1,2', type=lambda s: [float(item) for item in s.split(',')], default=[0, ])
parser.add_argument('N', type=int, help='Number of agents')
parser.add_argument('Nrea', type=int, help='Number of realitzations to perform')

args = parser.parse_args()

pi1, pi2, q1, q2, l, lci, ci_kwargs, N, Nrea = args.pi1, args.pi2, args.q1, args.q2, args.l, args.lci, args.ci_kwargs, args.N, args.Nrea
Nsites = 2
statFrom = 1000
simIters = 2000
getEvery = 50

ci_kwargs[0] = int(ci_kwargs[0])

ci_kwargs_chain = '_'.join([str(cikw) for cikw in ci_kwargs])
filename = f'stat_data_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_lci_{lci}_cikw_{ci_kwargs_chain}.csv'

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/stationary_distributions/data'
    if not os.path.exists(path):
        call(f'mkdir -p {path}', shell=True)
else:
    path = '/data'

if os.path.exists(f'{path}/{filename}'):
    oldData = pd.read_csv(f'{path}/{filename}')
    existingReas = pd.unique(oldData['rea'])
    maxRea = max(existingReas)
else:
    maxRea = 0

# Working directory and simulation execution files  
wd = os.getcwd()
# input to Fortran code route:
# froute = "/home/david/Desktop/Uni_code/TFM_code/clean_version_ci/"
froute = "/Users/david/Desktop/Uni_code/TFM_code/clean_version_ci/"
fin_file = 'input_template.txt'
fex_file = 'main.x'
f_file = 'main.f90'

# very generic initial condition; add parser argument if want to change it...
if l < 1.0 and pi1 > 0.0 and pi2 > 0.0:
    bots_per_site = [N, 0, 0]
elif l == 1.0 or (pi1 == 0.0 and pi2 == 0.0):
    bots_per_site = [0, N/2, N/2]

# Fortran code uses cimode labels 1,2,3 instead of 0,1,2; so...
cimode = int(ci_kwargs[0]+1)
change_sim_input(froute, fin_file, (pi1, pi2), (q1, q2), l, simIters, Nsites, N, bots_per_site, 'N', cimode=cimode)
if cimode > 1:
    change_sim_input(froute, fin_file, ci_x0=ci_kwargs[1], ci_a=ci_kwargs[2])

# Execute simulations:
os.chdir(froute)
call("./"+fex_file+f" {randint(0,100000000)} {Nrea}", shell=True)
os.chdir(wd)

# Save the time evolutions:
call(f'tar -xzf {froute}time_evo_csv.tar.gz', shell=True)
rea, fs = [], [[],[],[]]
for i in range(1,Nrea+1):
    time_evo = pd.read_csv(f'time_evo_csv/time_evo_rea_{str(i).zfill(3)}.csv')
    time_evo = time_evo.iloc[statFrom::getEvery, :]
    for j,label in enumerate(['f0', 'f1', 'f2']):
        fs[j].extend(list(time_evo[label]))
    rea.extend([maxRea+i]*int((simIters-statFrom)/getEvery + 1))


newData = pd.DataFrame({'rea':rea})
for i, label in enumerate(['f0', 'f1', 'f2']):
    newData[label] = fs[i]

if os.path.exists(f'{path}/{filename}'):
    finalDf = pd.concat([oldData, newData])
    finalDf.to_csv(f'{path}/{filename}', index=False)
else:
    newData.to_csv(f'{path}/{filename}', index=False)
    
call('rm -r time_evo_csv/', shell=True)