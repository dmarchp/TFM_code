import numpy as np
from subprocess import call
import glob
import sys
sys.path.append('../')
from package_global_functions import *
from evo_to_stationary import intEvo, simEvo

# same function as in plot_evos.py
def getTimeEvosPath():
    extSSDpath = getExternalSSDpath()
    if os.path.exists(extSSDpath):
        path = extSSDpath + getProjectFoldername() + '/evo_to_stationary/time_evos_dif_cond'
    else:
        path = '/time_evos_dif_cond'
    return path

pi1, pi2, q1, q2 = 0.25, 0.25, 7, 10

# np.random.seed(349)

for N in [5000, ]:
    for pi in [0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35]:
        print(pi)
    # ls = [0.01, 0.05, 0.1, 0.15, 0.18, 0.2, 0.22, 0.25, 0.3, 0.6, 0.9]
    # if N == 1000:
    #     ls = [0.01, 0.05, 0.09, 0.1, 0.11, 0.13, 0.15, 0.3, 0.6, 0.9]
    # elif N == 35:
    #     ls = [0.01, 0.05, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.17, 0.2, 0.23, 0.25, 0.3, 0.6, 0.9]
    # Naux = 1000
    # files = glob.glob(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q}_q2_{q}_l_*_ic_thirds')
    # ls = sorted([float(file.split('/')[-1].split('_')[14]) for file in files])
        ls = np.linspace(0.0, 0.99, 100)
        for l in ls:
            # call(f'python evo_to_stationary.py {pi1} {pi2} {q} {q} {l} {N} T {np.random.randint(1,1000000)}', shell=True)
            # simEvo(pi1, pi2, q1, q2, l, N, ic='N', bots_per_site = [N, 0, 0], max_time = 1000, Nrea=25)
            simEvo(pi, pi, q1, q2, l, N, ic='N', bots_per_site = [N, 0, 0], max_time = 1000, Nrea=25)