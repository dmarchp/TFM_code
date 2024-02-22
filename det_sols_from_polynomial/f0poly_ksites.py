import numpy as np
from scipy.optimize import bisect
import argparse
import itertools
from f0poly_sols_clean import f_i


def f0poly(f0: float, pis: np.array, qs: np.array, l: float):
    prod1 = 1.0
    for q in qs:
        prod1 *= (1/q - l*f0)
    sum1 = 0.0
    for i,pi in enumerate(pis):
        prod2 = 1.0
        qsf = qs[qs != qs[i]]
        for q in qsf:
            prod2 *= (1/q - l*f0)
        sum1 += pi*prod2
    return (1-f0)*prod1 - (1-l)*f0*sum1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: np.array([float(item) for item in s.split(',')]))
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: np.array([float(item) for item in s.split(',')]))
    parser.add_argument('l', type=float, help='interdependence (lambda)')
    args = parser.parse_args()
    pis, qs, l = args.pis, args.qs, args.l

    f0vals = np.arange(0.0,1.001,0.001)
    f0poly_vals = f0poly(f0vals, pis, qs, l)
    f0poly_vals_splitted = [list(g) for i, g in itertools.groupby(f0poly_vals, lambda x: x<0)]
    prev_bi = 0
    f0_sols = []
    fs_sols = []
    for i in range(len(f0poly_vals_splitted)-1):
        # a,b = f0poly_vals_splitted[i][-1], f0poly_vals_splitted[i+1][0]
        # print(a,b)
        ai, bi = prev_bi+len(f0poly_vals_splitted[i])-1, prev_bi+len(f0poly_vals_splitted[i])
        prev_bi = bi
        a, b = f0vals[ai], f0vals[bi]
        f0 = bisect(f0poly, a, b, args=(pis, qs, l))
        f0_sols.append(f0)
        fs_sols.append([f0,])
        for j in range (len(pis)): #site j+1, sites j+2, ...
            fs_sols[i].append(f_i(j+1, f0, pis, qs, l, mu=0.0))
        print(fs_sols[i])



if __name__ == '__main__':
    main()