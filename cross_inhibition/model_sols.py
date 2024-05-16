import argparse
import numpy as np
from scipy.optimize import fsolve, bisect

def cross_in_func(pop,*kwargs):
    # kwargs 
    # first: linear, sigmoid 1 or 2...
    # second: x0
    # third: a
    # fouth: make superior part of the sigmoid linear (True) or not
    if not kwargs or kwargs[0] == 0 or kwargs[0] == 'lin':
        return pop
    elif kwargs[0] == 1 or kwargs[0] == 'sigmoid1':
        x0, a = kwargs[1], kwargs[2]
        cival = 1/(1+np.exp(-a*(pop-x0))) 
        if len(kwargs) == 4 and kwargs[3]:
            cival = min(cival, pop)
        return cival
    elif kwargs[0] == 2 or kwargs[0] == 'sigmoid2':
        x0, a = kwargs[1], kwargs[2]
        return 1*pop/(1+np.exp(-a*(pop-x0)))


#### Non linear cross inhibition:
def fs_evo_eq_fxp_v2(fs, pis, qs, l, lci, ci_kwargs):
    f0 = 1 - sum(fs)
    dfsdt = []
    for i in range(len(fs)):
        site_i = i
        dfdt = f0*((1-l)*pis[i]+l*fs[site_i]) - fs[site_i]/qs[i] #- lci*fs[site_i]*(sum(fs[1:site_i])+sum(fs[site_i+1:]))
        for j in range(len(fs)):
            site_j = j
            if site_j != site_i:
                dfdt += -lci*fs[site_i]*cross_in_func(fs[site_j],*ci_kwargs)
        dfsdt.append(dfdt)
    return dfsdt

def fs_evo_eq_fxp_v2_jac(fs, pis, qs, l, lci, ci_kwargs):
    x0, a = ci_kwargs[1], ci_kwargs[2]
    f1f1 = l - (1-l)*pis[0] - 2*l*fs[0] - l*fs[0]*fs[1] - 1/qs[0] - lci*cross_in_func(fs[1], *ci_kwargs)
    f1f2 = -(1-l)*pis[0] - l*fs[0] -lci*a*np.exp(-a*(fs[1]-x0))*cross_in_func(fs[1], *ci_kwargs)**2
    f2f1 = -(1-l)*pis[1] - l*fs[1] -lci*a*np.exp(-a*(fs[0]-x0))*cross_in_func(fs[0], *ci_kwargs)**2
    f2f2 = l - (1-l)*pis[1] - 2*l*fs[1] - l*fs[0]*fs[1] - 1/qs[1] - lci*cross_in_func(fs[0], *ci_kwargs)
    return np.array([[f1f1, f1f2], [f2f1, f2f2]])

def get_sols_nlinci():
    starters = [[0.8, 0.1], [0.1, 0.8], [0.3, 0.3]]
    for fs0 in starters:
        fxp = fsolve(fs_evo_eq_fxp_v2, fs0, args = (pis, qs, l, lci, ci_kwargs), fprime=fs_evo_eq_fxp_v2_jac, maxfev=1000)
        f0 = 1-sum(fxp)
        fs = [f0, *fxp]
        print(*fs)


#### Linear Cross Inhbition:
def f0_equation_linci(f0, pis, qs, l, lci, permutation):
    # as a solution of a second degree poly is involved, choose branch by setting +1 or -1
    Nsites = len(pis)
    rs = [1/q for q in qs]
    sumval = 0.0
    for i in range(Nsites):
        sqrtArg = ((l+lci)*f0 - rs[i] - lci)**2 - 4*lci*(1-l)*pis[i]*f0
        if sqrtArg < 0  and abs(sqrtArg) < 1e-8:
            sqrtArg = 0.0
        if sqrtArg >= 0:
            sumval += (rs[i] + permutation[i]*np.sqrt(sqrtArg))
        else:
            print(sqrtArg, np.sqrt(sqrtArg))
            sumval += (rs[i] + permutation[i]*np.sqrt(sqrtArg))
            print(sumval)
    sumval = sumval/(2*lci)
    return 1 - f0 + (Nsites*(l+lci)*f0-Nsites*lci)/(2*lci) - sumval

def f0_eq_sqrt_zeros(pi, q, l, lci):
    r = 1/q
    a = (l + lci)**2
    b = (-2*(l+lci)*(r+lci) - 4*lci*(1-l)*pi)
    c = (r+lci)**2
    arrel = np.sqrt(b**2 - 4*a*c)
    return (-b+arrel)/(2*a), (-b-arrel)/(2*a)

def falpha_linci(f0, pi, q, l, lci, branch):
    r = 1/q
    # rootval = np.sqrt(((l+lci)*f0 - r - lci)**2 - 4*lci*(1-l)*pi*f0)
    a = lci
    b = -r-lci+(l+lci)*f0
    c = f0*(1-l)*pi
    arrel = np.sqrt(b**2 - 4*a*c)
    # return (-b+arrel)/(2*a), (-b-arrel)/(2*a)
    return (-b + branch*arrel)/(2*a)

def get_sols_linci():
    permutations = (+1, +1), (+1, -1), (-1, +1), (-1, -1)
    f0s1 = f0_eq_sqrt_zeros(pis[0], qs[0], l, lci)
    f0s2 = f0_eq_sqrt_zeros(pis[1], qs[1], l, lci)
    f0sProb = sorted(f0s1 + f0s2)
    sols_f0_perm = {}
    for permutation in permutations:
        args = [pis, qs, l, lci, permutation]
        try:
            a = f0_equation_linci(0.0, *args)
        except RuntimeWarning:
            a = 0
        try:
            b = f0_equation_linci(f0sProb[0]-1e-6, *args)
        except:
            b = 0
        # if f0_equation_linci(0.0, *args)*f0_equation_linci(f0sProb[0]-1e-6, *args) < 0:
        if a*b < 0:
            c = bisect(f0_equation_linci, 0.0, f0sProb[0], args=(pis, qs, l, lci, permutation))
            sols_f0_perm[permutation] = c
    sols_fs_perm = {}
    for permutation,f0 in sols_f0_perm.items():
        f1 = falpha_linci(f0, pis[0], qs[0], l, lci, permutation[0])
        f2 = falpha_linci(f0, pis[1], qs[1], l, lci, permutation[1])
        sols_fs_perm[permutation] = [f0, f1, f2]
        # print(permutation)
        print(*sols_fs_perm[permutation])
    # return sols_f0_perm, sols_fs_perm



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-l', help='lambda', type=float)
    parser.add_argument('-lci', help='lambda ci', type=float)
    parser.add_argument('-ci_kwargs', help='(cimode; ci_x0, ci_a)', type=lambda s: [float(item) for item in s.split(',')], default=[0, ])
    args = parser.parse_args()
    pis, qs, l, lci, ci_kwargs = args.pis, args.qs, args.l, args.lci, args.ci_kwargs
    ci_kwargs[0] = int(ci_kwargs[0])
    if len(pis) != len(qs):
        print('Input number of pis different from qualities. Aborting.')
        exit()
    Nsites = len(pis)
    if ci_kwargs[0] != 0:
        get_sols_nlinci()
    elif ci_kwargs[0] == 0:
        get_sols_linci()
