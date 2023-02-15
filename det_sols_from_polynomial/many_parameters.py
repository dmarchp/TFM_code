import subprocess
import numpy as np
import pandas as pd

subprocess.call('python f0poly_sols_clean.py 0.1 0.1 7 10 0.5 > sols.dat', shell=True)
with open('sols.dat', 'r') as file:
    sols = [float(f) for f in file.readline().split()]

print(sols)



def computeSimetricMap_df(q1, q2, dpi=0.01, pi_lims = (0.01, 0.99),dl=0.01, l_lims = (0.01,0.99)):
    # future dataframe:
    map = {'pi':[], 'l':[], 'f0':[], 'f1':[], 'f2':[]}
    # loop over phase diagram
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    Nls = int((l_lims[1] - l_lims[0])/dl) + 1
    for i in range(Npis):
        pi = pi_lims[0] + i*dpi
        for j in range(Nls):
            l = l_lims[0] + j*dl
            subprocess.call(f'python f0poly_sols_clean.py {pi} {pi} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
            map['pi'].append(pi), map['l'].append(l)
            map['f0'].append(sols[0]), map['f1'].append(sols[1]), map['f2'].append(sols[2])
    # build and save datagrame
    df = pd.DataFrame(map)
    pd.to_csv(f'res_files/map_sim_q1_{q1}_q2_{q2}.csv')

# potser fer un mesh seria mes logic........
def computeSimetricMap_mesh(q1, q2, dpi=0.01, pi_lims = (0.01, 0.99),dl=0.01, l_lims = (0.01,0.99)):
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    Nls = int((l_lims[1] - l_lims[0])/dl) + dl + 1
    x_pi = np.linspace(0, 1, Npis)
    y_l = np.linspace(0, 1, y_l)


def computeAsimetricMap_df(q1, q2, l, dpi=0.01, pi_lims = (0.01, 0.99)):
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    pis = np.linspace(pi_lims[0], pi_lims[1], Npis)
    # future dataframe:
    map = {'pi1':[], 'pi2':[], 'f0':[], 'f1':[], 'f2':[]}
    for pi1 in pis:
        for pi2 in pis:
            subprocess.call(f'python f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
            map['pi1'].append(pi1), map['pi2'].append(pi2)
            map['f0'].append(sols[0]), map['f1'].append(sols[1]), map['f2'].append(sols[2])
    df = pd.DataFrame(map)
    pd.to_csv(f'res_files/map_asim_q1_{q1}_q2_{q2}_l_{l}.csv')


