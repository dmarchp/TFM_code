import pandas as pd
import os
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
parser.add_argument('Nrea', type=int, help='Number of realitzations to perform')
parser.add_argument('inSeed', type=int, help='seed')

args = parser.parse_args()

pi1, pi2, q1, q2, l, N, Nrea, inSeed = args.pi1, args.pi2, args.q1, args.q2, args.l, args.N, args.Nrea, args.inSeed
Nsites = 2
seed(inSeed)
statFrom = 1000
simIters = 2000
getEvery = 20

filename = f'stat_data_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv'

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
froute = "/home/david/Desktop/Uni_code/TFM_code/clean_version/"
fin_file = 'input_template.txt'
fex_file = 'main.x'
f_file = 'main.f90'

call(f"sed -i '17s/.*/lambda = {l}/' "+froute+fin_file, shell=True)
call(f"sed -i '27s/.*/pi(:) = {pi1} {pi2}/' "+froute+fin_file, shell=True)
call(f"sed -i '30s/.*/q(:) = {q1} {q2}/' "+froute+fin_file, shell=True)
call(f"sed -i '13s/.*/N_sites = {Nsites}/' "+froute+fin_file, shell=True)
call(f"sed -i '12s/.*/N_bots = {N}/' "+froute+fin_file, shell=True)
call(f"sed -i '14s/.*/max_time = {simIters}/' "+froute+fin_file, shell=True)
zero_sites_str = ''
for i in range(Nsites):
    zero_sites_str += '0 '
call(f"sed -i '35s/.*/bots_per_site = {N} "+zero_sites_str+"/' "+froute+fin_file, shell=True)

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
