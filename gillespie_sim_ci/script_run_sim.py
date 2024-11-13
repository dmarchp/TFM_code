from subprocess import call
import os
import sys
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    resPath = extSSDpath + getProjectFoldername() + '/gillespie_sim_ci/results'
else:
    resPath = '/results'

q1, q2 = 10.0, 10.0
ic = 'p00-51-49'
# ic = 'p00-80-20'

pis = [0.0, 0.001, 0.01]
# pis = [0.001, ]

ls = [0.101, ]
# ls = [0.11, 0.2, 0.6]

for pi in pis:
    for l in ls:
        call(f'python LES_model_gill.py -pis {pi},{pi} -qs {q1},{q2} -l {l} -lci 0.0 -N 5000 -maxTime 500.0 -Nrea 20 -ic {ic} --time_evo', shell=True)
        folder = f'sim_results_evos_pis_{pi}_{pi}_qs_{q1}_{q2}_l_{l}_lci_0.0_cikw_0_N_5000_ic_{ic}'
        if os.path.exists(f'{folder}.tar.gz'):
            call(f'tar -xf {folder}.tar.gz', shell=True)
            call(f'mv {folder} {resPath}/', shell=True)
            call(f'rm {folder}.tar.gz', shell=True)
        else:
            print('aaa ')
        # call(f'rm -r {folder}', shell=True)
