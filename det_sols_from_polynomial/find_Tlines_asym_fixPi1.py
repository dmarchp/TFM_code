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
parser.add_argument('pi1', type=float, help='site 1 probability discovery (pi1)')
parser.add_argument(
    'x', type=float, help='factor between f1 and f2, f2 = x*f1')
parser.add_argument('--mu', type=float, default=0.0, help='independence on the quality assesment; 0 full indep.')
parser.add_argument('--Q', type=int, default=0, help='Consensus def. 0: usual f2-x*f1, 1: mod f2-x*max(f0,f1), 2: f2 thresh, 3: mod2 f2-max(f0,xf1)')
args = parser.parse_args()

q1, q2, pi1, x, mu, Q = args.q1, args.q2, args.pi1, args.x, args.mu, args.Q


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

# iteratively go through all pi2s and find the lambda, if it exits; else NaN
pi2_lims = (0.01, 0.5)
dpi = 0.01
Npis = int((pi2_lims[1] - pi2_lims[0])/dpi) + 1
pi2s = np.linspace(pi2_lims[0], pi2_lims[1], Npis)
pi2s = np.around(pi2s, 2)
pi2s_inf = np.linspace(0.001, 0.009, 9)
pi2s = np.append(pi2s_inf, pi2s)
lambdas = []
lambdas_solve_lims = (1e-10, 0.99)

last_pi2_w_sol = None
for pi2 in pi2s:
    try:
        lamb = bisect(consensus_eq, lambdas_solve_lims[0], lambdas_solve_lims[1], args=(pi1, pi2, q1, q2, x, mu))
    except ValueError:
        lamb = float('nan')
    if not last_pi2_w_sol and np.isnan(lamb):
        last_pi2_w_sol = pi2-dpi
    lambdas.append(lamb)

# extra pi2s
if last_pi2_w_sol:
    dpi_smaller = dpi/10
    pi2_lims = (last_pi2_w_sol+dpi_smaller, last_pi2_w_sol+dpi-dpi_smaller)
    Npis = int((pi2_lims[1] - pi2_lims[0])/dpi_smaller) + 1
    pi2s_extra = np.linspace(pi2_lims[0], pi2_lims[1], Npis)
    pi2s = np.around(pi2s, 4)
    lambdas_extra = []
    for pi2 in pi2s_extra:
        try:
            lamb = bisect(consensus_eq, lambdas_solve_lims[0], lambdas_solve_lims[1], args=(pi1, pi2, q1, q2, x, mu))
        except ValueError:
            lamb = float('nan')
        lambdas_extra.append(lamb)
    pi2s = np.append(pi2s, pi2s_extra)
    lambdas.extend(lambdas_extra)

df = pd.DataFrame({'pi2':pi2s, 'lambda':lambdas})
df = df.sort_values(by='pi2')

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    path = '/res_files'

if not os.path.exists(path):
    call(f'mkdir -p {path}', shell=True) # no faria falta la -p ...

if mu == 0.0:
    fileMuLabel = ''
else:
    fileMuLabel = f'_mu_{mu}'

filename = 'Tline' + fileQlabel + f'_asym_fixPi1_pi1_{pi1}_q1_{round(q1,2)}_q2_{round(q2,2)}' + fileMuLabel
if Q == 0 or Q == 1 or Q == 3:
    filename += f'_f2_{int(x)}f1'
elif Q == 2:
    filename += '_f2_x_2'
filename += '.csv'

print(filename)
df.to_csv(f'{path}/{filename}', index=False)

# df.to_csv(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv', index=False)