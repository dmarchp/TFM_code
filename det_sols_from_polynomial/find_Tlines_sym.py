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
parser.add_argument('--mu', type=float, default=0.0, help='independence on the quality assesment; 0 full indep.')
parser.add_argument('--Q', type=int, default=0, help='Consensus def. 0: usual f2-x*f1, 1: mod f2-x*max(f0,f1), 2: f2 thresh, 3: mod2 f2-max(f0,xf1)')
args = parser.parse_args()

q1, q2, x, mu, Q = args.q1, args.q2, args.x, args.mu, args.Q

def consensus_usual_eq(l, pi1, pi2, q1, q2, x, mu):
    'usual definition of consensus'
    'equation to be solved numerically'
    'instead of involving the strange F factor, this uses de usual f2-x*f1'
    _, f0, _ = f0_lambda_neq_0(pi1, pi2, q1, q2, l, mu)
    f1, f2 = f_i(1, f0, [pi1, pi2], [q1, q2], l, mu), f_i(2, f0, [pi1, pi2], [q1, q2], l, mu)
    return f2 - x*f1

def consensus_mod_eq(l, pi1, pi2, q1, q2, x, mu):
    'modified definition of consensus, with max(f0,f1)'
    'equation to be solved numerically'
    _, f0, _ = f0_lambda_neq_0(pi1, pi2, q1, q2, l, mu)
    f1, f2 = f_i(1, f0, [pi1, pi2], [q1, q2], l, mu), f_i(2, f0, [pi1, pi2], [q1, q2], l, mu)
    return f2 - x*max(f0, f1)

def consensus_mod2_eq(l, pi1, pi2, q1, q2, x, mu):
    'modification to consensus mod, max(f0, x*f1) instead of x*max(f0,f1)'
    'equation to ve solved numerically'
    _, f0, _  = f0_lambda_neq_0(pi1, pi2, q1, q2, l, mu)
    f1, f2 = f_i(1, f0, [pi1, pi2], [q1, q2], l, mu), f_i(2, f0, [pi1, pi2], [q1, q2], l, mu)
    return f2 - max(f0, x*f1)

def consensus_f2_eq(l, pi1, pi2, q1, q2, x, mu):
    'modified definition of consensus, just considering f2 greater than a threshold'
    _, f0, _ = f0_lambda_neq_0(pi1, pi2, q1, q2, l, mu)
    f1, f2 = f_i(1, f0, [pi1, pi2], [q1, q2], l, mu), f_i(2, f0, [pi1, pi2], [q1, q2], l, mu)
    return f2 - x/(x+1)

# def pi2_lambda_eq_0(pi1, q1, q2):
#     'when lambda == 0, an exact equation exists - no need for a numerical solution'
#     pi2 = pi1*q1/q2
#     return pi2

if Q == 0:
    consensus_eq = consensus_usual_eq
    fileQlabel = ''
elif Q == 1:
    consensus_eq = consensus_mod_eq
    fileQlabel = '_Qmod'
elif Q == 2:
    consensus_eq = consensus_f2_eq
    fileQlabel = '_Qmodf2'
elif Q == 3:
    consensus_eq = consensus_mod2_eq
    fileQlabel = '_Qmod2'

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
        lamb = bisect(consensus_eq, lamb_solve_lims[0], lamb_solve_lims[1], args=(pi, pi, q1, q2, x, mu))
    except ValueError:
        lamb = float('nan')
    if not np.isnan(lamb) and not first_pi_w_sol:
        first_pi_w_sol = pi
    if not np.isnan(lamb):
        last_pi_w_sol = pi
    lambs.append(lamb)

# extra pis to the beggining:
if first_pi_w_sol:
    dpi_smaller = dpi/10
    pi_lims = (first_pi_w_sol-dpi+dpi_smaller, first_pi_w_sol-dpi_smaller)
    Npis = int((pi_lims[1] - pi_lims[0])/dpi_smaller) + 1
    pis_ex = np.linspace(pi_lims[0], pi_lims[1], Npis)
    pis_ex = np.around(pis_ex, 3)
    lambs_ex = []
    for pi in pis_ex:
        try:
            lamb = bisect(consensus_eq, lamb_solve_lims[0], lamb_solve_lims[1], args=(pi, pi, q1, q2, x, mu))
        except ValueError:
            lamb = float('nan')
        lambs_ex.append(lamb)
    pis = np.append(pis_ex, pis)
    lambs_ex.extend(lambs)
    lambs = lambs_ex

# extra pis to the end:
if last_pi_w_sol < pis[-1]:
    dpi_smaller = dpi/10
    pi_lims = (last_pi_w_sol+dpi_smaller, + last_pi_w_sol+dpi-dpi_smaller)
    Npis = int((pi_lims[1] - pi_lims[0])/dpi_smaller) + 1
    pis_ex = np.linspace(pi_lims[0], pi_lims[1], Npis)
    pis_ex = np.around(pis_ex, 3)
    lambs_ex = []
    for pi in pis_ex:
        try:
            lamb = bisect(consensus_eq, lamb_solve_lims[0], lamb_solve_lims[1], args=(pi, pi, q1, q2, x, mu))
        except ValueError:
            lamb = float('nan')
        lambs_ex.append(lamb)
    lambs.extend(lambs_ex)
    pis = np.append(pis, pis_ex)

# Appendix: let's see how this works out, and maybe "extra pis to the start" can go...
# Solution when pi = 0
# for the moment I do nothing here, i will add manually the solution if necessary, when ploting the tlines


df = pd.DataFrame({'pi':pis, 'lambda':lambs})
df = df.sort_values(by='pi')

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    path = '/res_files'

if not os.path.exists(path):
    call(f'mkdir -p {path}', shell=True)


if mu == 0.0:
    fileMuLabel = ''
else:
    fileMuLabel = f'_mu_{mu}'

filename = 'Tline' + fileQlabel + f'_sym_pis_q1_{round(q1,2)}_q2_{round(q2,2)}' + fileMuLabel
if Q == 0 or Q == 1 or Q == 3:
    filename += f'_f2_{int(x)}f1'
elif Q == 2:
    filename += '_f2_x_2'
filename += '.csv'

print(filename)
df.to_csv(f'{path}/{filename}', index=False)
