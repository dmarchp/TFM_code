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


def consensus_usual_eq(q1, pi1, pi2, l, q2, x, mu):
    'usual definition of consensus'
    'equation to be solved numerically'
    'instead of involving the strange F factor, this uses de usual f2-x*f1'
    _, f0, _ = f0_lambda_neq_0(pi1, pi2, q1, q2, l, mu)
    f1, f2 = f_i(1, f0, [pi1, pi2], [q1, q2], l, mu), f_i(2, f0, [pi1, pi2], [q1, q2], l, mu)
    return f2 - x*f1

consensus_eq = consensus_usual_eq


q2s = [10.0, 20.0, 30.0, 40.0]
q1s = []
pi1, pi2, l, x, mu = 0.1, 0.1, 0.5, 2, 0.0

for q2 in q2s:
    q1_solve_lims = [1.0,q2]
    q1 = bisect(consensus_eq, q1_solve_lims[0], q1_solve_lims[1], args=(pi1, pi2, l, q2, x, mu))
    q1s.append(q1)

print(q1s)
