import numpy as np
from subprocess import call
import glob
import sys
sys.path.append('../')
from package_global_functions import *

# same function as in plot_evos.py
def getTimeEvosPath():
    extSSDpath = getExternalSSDpath()
    if os.path.exists(extSSDpath):
        path = extSSDpath + getProjectFoldername() + '/evo_to_stationary/time_evos_dif_cond'
    else:
        path = '/time_evos_dif_cond'
    return path

pi1, pi2, q = 0.0, 0.0, 5

np.random.seed(349)

for N in [35, ]:
    # ls = [0.01, 0.05, 0.1, 0.15, 0.18, 0.2, 0.22, 0.25, 0.3, 0.6, 0.9]
    # if N == 1000:
    #     ls = [0.01, 0.05, 0.09, 0.1, 0.11, 0.13, 0.15, 0.3, 0.6, 0.9]
    # elif N == 35:
    #     ls = [0.01, 0.05, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.17, 0.2, 0.23, 0.25, 0.3, 0.6, 0.9]
    # Naux = 1000
    files = glob.glob(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q}_q2_{q}_l_*_ic_thirds')
    ls = sorted([float(file.split('/')[-1].split('_')[14]) for file in files])
    for l in ls:
        call(f'python evo_to_stationary.py {pi1} {pi2} {q} {q} {l} {N} T {np.random.randint(1,1000000)}', shell=True)