import argparse
from f0poly_sols_clean import f0_lambda_neq_0, f0_lambda_eq_0, f_i
from scipy.optimize import bisect, newton
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('q1', type=int, help='site 1 quality')
parser.add_argument('q2', type=int, help='site 2 quality')
parser.add_argument('l', type=float, help='interdependence (lambda)')
parser.add_argument('x', type=float, help='factor between f1 and f2, f2 = x*f1')
args = parser.parse_args()

q1, q2, l, x = args.q1, args.q2, args.l, args.x

# aquesta funció té el problema de tenir dues arrels a l'interval pi2 (0,0.5)
# aleshores per fer bisecció s'ha d'anar desplaçant el límit superior per poder tenir canvi de signe
# i a més no acabar a la segona arrel, que no interessa
def eq_lambda_neq_0(pi2, pi1, q1, q2, l, x):
    'equation to be solved numerically when lambda != 0'
    _, f0, _ = f0_lambda_neq_0(pi1, pi2, q1, q2, l)
    F = 1/l
    F = F*(1-x*pi1*q1/(pi2*q2))
    F = F/(q1-x*pi1*q1/pi2)
    # print(f0, F)
    return f0 - F


# print(eq_lambda_neq_0(0.00001, 0.1, q1, q2, l, x))
# print(eq_lambda_neq_0(0.06, 0.1, q1, q2, l, x))

# pi2 = bisect(eq_lambda_neq_0, 0.00001, 0.06, args=(0.1, q1, q2, l, x))
# print(pi2)
# pi2 = newton(eq_lambda_neq_0, 0.04899, args=(0.1, q1, q2, l, x))
# print(pi2)

# pi1 = 0.1
# dpi = 0.01
# pi_lims = (0.01, 0.5)
# Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
# pi2s = np.linspace(pi_lims[0], pi_lims[1], Npis)
# eqvals = [eq_lambda_neq_0(pi2,pi1,q1,q2,l,x) for pi2 in pi2s]
# fig, ax = plt.subplots()
# ax.plot(pi2s, eqvals)
# ax.set_yscale('symlog')
# plt.show()

#############

def eq_lambda_neq_0_v2(pi2, pi1, q1, q2, l, x):
    'equation to be solved numerically when lambda != 0'
    'instead of involving the strange F factor, this uses de usual f2-x*f1'
    _, f0, _ = f0_lambda_neq_0(pi1, pi2, q1, q2, l)
    f1, f2 = f_i(1, f0, [pi1,pi2], [q1,q2], l), f_i(2, f0, [pi1,pi2], [q1,q2], l)
    return f2 - x*f1

pi1 = 0.05
print(eq_lambda_neq_0_v2(-0.49, pi1, q1, q2, l, x))
print(eq_lambda_neq_0_v2(0.5, pi1, q1, q2, l, x))

try:
    pi2 = bisect(eq_lambda_neq_0_v2, -0.49, 0.5, args=(pi1, q1, q2, l, x))
    print(pi2)
except ValueError:
    print('no root')