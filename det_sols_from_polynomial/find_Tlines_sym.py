import argparse
from f0poly_sols_clean import f0_lambda_neq_0, f0_lambda_eq_0, f_i
from scipy.optimize import bisect, newton
from subprocess import call
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('../')
from package_global_functions import *

parser = argparse.ArgumentParser()
parser.add_argument('q1', type=float, help='site 1 quality')
parser.add_argument('q2', type=float, help='site 2 quality')
parser.add_argument(
    'x', type=float, help='factor between f1 and f2, f2 = x*f1')
args = parser.parse_args()

q1, q2, x = args.q1, args.q2, args.x

def consensus_eq(l, pi1, pi2, q1, q2, x):
    'equation to be solved numerically'
    'instead of involving the strange F factor, this uses de usual f2-x*f1'
    _, f0, _ = f0_lambda_neq_0(pi1, pi2, q1, q2, l)
    f1, f2 = f_i(1, f0, [pi1, pi2], [q1, q2], l), f_i(2, f0, [pi1, pi2], [q1, q2], l)
    return f2 - x*f1

# def pi2_lambda_eq_0(pi1, q1, q2):
#     'when lambda == 0, an exact equation exists - no need for a numerical solution'
#     pi2 = pi1*q1/q2
#     return pi2


# iteratively go through all pi12s and finde the lambda, if it exits; else NaN
pi_lims = (0.01, 0.5)
dpi = 0.01
Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
pis = np.linspace(pi_lims[0], pi_lims[1], Npis)
pis = np.around(pis, 2)
lambs = []
lamb_solve_lims = (1e-10, 0.99)

first_pi_w_sol = None
for pi in pis:
    try:
        lamb = bisect(consensus_eq, lamb_solve_lims[0], lamb_solve_lims[1], args=(pi, pi, q1, q2, x))
    except ValueError:
        lamb = float('nan')
    if not np.isnan(lamb) and not first_pi_w_sol:
        first_pi_w_sol = pi
    lambs.append(lamb)

# extra pis:
if first_pi_w_sol:
    dpi_smaller = dpi/10
    pi_lims = (first_pi_w_sol-dpi+dpi_smaller, first_pi_w_sol-dpi_smaller)
    Npis = int((pi_lims[1] - pi_lims[0])/dpi_smaller) + 1
    pis_ex = np.linspace(pi_lims[0], pi_lims[1], Npis)
    pis_ex = np.around(pis_ex, 3)
    lambs_ex = []
    for pi in pis_ex:
        try:
            lamb = bisect(consensus_eq, lamb_solve_lims[0], lamb_solve_lims[1], args=(pi, pi, q1, q2, x))
        except ValueError:
            lamb = float('nan')
        lambs_ex.append(lamb)
    pis = np.append(pis_ex, pis)
    lambs_ex.extend(lambs)
    lambs = lambs_ex


df = pd.DataFrame({'pi':pis, 'lambda':lambs})
df = df.sort_values(by='pi')

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    path = '/res_files'

if not os.path.exists(path):
    call(f'mkdir -p {path}', shell=True)

df.to_csv(f'{path}/Tline_sym_pis_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv', index=False)
