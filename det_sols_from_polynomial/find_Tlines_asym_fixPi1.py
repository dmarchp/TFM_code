import argparse
from f0poly_sols_clean import f0_lambda_neq_0, f0_lambda_eq_0, f_i
from scipy.optimize import bisect, newton
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('q1', type=int, help='site 1 quality')
parser.add_argument('q2', type=int, help='site 2 quality')
parser.add_argument('pi1', type=float, help='site 1 probability discovery (pi1)')
parser.add_argument(
    'x', type=float, help='factor between f1 and f2, f2 = x*f1')
args = parser.parse_args()

q1, q2, pi1, x = args.q1, args.q2, args.pi1, args.x


def consensus_eq(l, pi1, pi2, q1, q2, x):
    _, f0, _ = f0_lambda_neq_0(pi1, pi2, q1, q2, l)
    f1, f2 = f_i(1, f0, [pi1, pi2], [q1, q2], l), f_i(
        2, f0, [pi1, pi2], [q1, q2], l)
    return f2 - x*f1


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
        lamb = bisect(consensus_eq, lambdas_solve_lims[0], lambdas_solve_lims[1], args=(pi1, pi2, q1, q2, x))
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
    pi2s = np.around(pi2s, 2)
    lambdas_extra = []
    for pi2 in pi2s_extra:
        try:
            lamb = bisect(consensus_eq, lambdas_solve_lims[0], lambdas_solve_lims[1], args=(pi1, pi2, q1, q2, x))
        except ValueError:
            lamb = float('nan')
        lambdas_extra.append(lamb)
    pi2s = np.append(pi2s, pi2s_extra)
    lambdas.extend(lambdas_extra)

df = pd.DataFrame({'pi2':pi2s, 'lambda':lambdas})
df = df.sort_values(by='pi2')
df.to_csv(f'res_files/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv', index=False)