import argparse
import math #, cmath
from numpy import isclose

parser = argparse.ArgumentParser()

parser.add_argument('pi1', type=float, help='site 1 quality')
parser.add_argument('pi2', type=float, help='site 2 quality')
parser.add_argument('q1', type=float, help='site 1 quality')
parser.add_argument('q2', type=float, help='site 2 quality')
parser.add_argument('l', type=float, help='interdependence (lambda)')
parser.add_argument('--mu', type=float, default=0.0, help='assessment indepencence; 0 for full indep.')

# parser.add_argument("-v", "--verbose", help="increase output verbosity",
#                     action="store_true")

parser.add_argument("-v", "--verbosity", action="count", default=0,
                    help="increase output verbosity")


# ------------ solution to the third degree poly, if lambda != 0.0 ----------
def f0_lambda_neq_0(pi1, pi2, q1, q2, l, mu):
    # r1, r2 = 1/q1, 1/q2
    K, q0 = q2, 1.0
    r1 = q0*(mu/K + (1-mu)/q1)
    r2 = q0*(mu/K + (1-mu)/q2)
    # global pi1, pi2, q1, q2, r1, r2, l
    # a f0**3 + b f0**2 + c f0 + d = 0
    a = -l**2
    b = l**2 + l*(r1+r2) + l*(1-l)*(pi1+pi2)
    c = -(1-l)*(pi1*r2 + pi2*r1) - l*(r1 + r2) - r1*r2
    d = r1*r2
    # step 1: delta0 and elta 1
    delta0 = b**2 - 3*a*c
    delta1 = 2*b**3 - 9*a*b*c + 27*a**2*d
    # step 2: computation of C:
    if delta0 == 0.0 and delta1 != 0.0:
        C = delta1**(1/3) # cubic_root[(delta1 + sqrt(delta1**2+0))/2]
    elif delta0 == 0.0 and delta1 == 0.0:
        C = 1.0 # so in the next step delta0/C yields 0.0 instead of NaN (0.0/0.0)
    else:
        radicand0 = delta1**2 - 4*delta0**3
        if radicand0 < 0:
            root0 = complex(0,math.sqrt(-1*radicand0))
        else:
            root0 = complex(math.sqrt(radicand0),0)
        radicand1 = (delta1 + root0)/2
        C = radicand1**(1/3)
    # 3: Final solution
    ksi = complex(-1, math.sqrt(3))/2
    f0_roots, f0_roots_abs = [], []
    for k in range(3):
        f0_root = -1/(3*a)*(b + ksi**k*C + delta0/(C*ksi**k))
        f0_roots.append(f0_root), f0_roots_abs.append(abs(f0_root))
    return f0_roots_abs

# ------------ solution to the third degree poly, if lambda != 0.0 but pi1=pi2=0 ----------
def f0_lambda_neq_0_pi_eq_0(q1, q2, l, mu):
    # r1, r2 = 1/q1, 1/q2
    K, q0 = q2, 1.0
    r1 = q0*(mu/K + (1-mu)/q1)
    r2 = q0*(mu/K + (1-mu)/q2)
    # global pi1, pi2, q1, q2, r1, r2, l
    # a f0**3 + b f0**2 + c f0 + d = 0
    a = -l**2
    b = l**2 + l*(r1+r2)
    c = - l*(r1 + r2) - r1*r2
    d = r1*r2
    # step 1: delta0 and elta 1
    delta0 = b**2 - 3*a*c
    delta1 = 2*b**3 - 9*a*b*c + 27*a**2*d
    # step 2: computation of C:
    if delta0 == 0.0 and delta1 != 0.0:
        C = delta1**(1/3) # cubic_root[(delta1 + sqrt(delta1**2+0))/2]
    elif delta0 == 0.0 and delta1 == 0.0:
        C = 1.0 # so in the next step delta0/C yields 0.0 instead of NaN (0.0/0.0)
    else:
        radicand0 = delta1**2 - 4*delta0**3
        if radicand0 < 0:
            root0 = complex(0,math.sqrt(-1*radicand0))
        else:
            root0 = complex(math.sqrt(radicand0),0)
        radicand1 = (delta1 + root0)/2
        C = radicand1**(1/3)
    # 3: Final solution
    ksi = complex(-1, math.sqrt(3))/2
    f0_roots, f0_roots_abs = [], []
    for k in range(3):
        f0_root = -1/(3*a)*(b + ksi**k*C + delta0/(C*ksi**k))
        f0_roots.append(f0_root), f0_roots_abs.append(abs(f0_root))
    return f0_roots_abs

# ---------- exact solution to f0, when lambda == 0.0 --------------------------
def f0_lambda_eq_0(pi1, pi2, q1, q2, l, mu):
    # global pi1, pi2, q1, q2, r1, r2, l
    K, q0 = q2, 1.0
    r1 = q0*(mu/K + (1-mu)/q1)
    r2 = q0*(mu/K + (1-mu)/q2)
    # return 1/(1+pi1*q1+pi2*q2)
    return 1/(1+pi1/r1+pi2/r2)

# ----------------------- Rest of the populations ------------------------------
def f_i(i, f0, pis, qs, l, mu):
    # global qs, rs, pis, l
    # rs = [1/q for q in qs]
    K, q0 = qs[-1], 1.0
    rs = [q0*(mu/K + (1-mu)/q) for q in qs]
    try:
        fi = (1-l)*pis[i-1]/(rs[i-1]/f0-l)
    except ZeroDivisionError:
        fi = float('nan') 
    # return (1-l)*pis[i-1]/(rs[i-1]/f0-l)
    return fi

def f2_pis_eq_0(f0, qs, l, mu):
    K, q0 = qs[-1], 1.0
    rs = [q0*(mu/K + (1-mu)/q) for q in qs]
    rho = 1 - f0
    r1, r2 = rs
    # rho, r1, r2 = 1-f0, 1/qs[0], 1/qs[1]
    if f0 == 1.0:
        return 0
    else:
        return (l*rho-r1)/(2*l-(r1+r2)/rho)
    
def f2_pis_eq_0_new(f0, qs, l, mu):
    K, q0 = qs[-1], 1.0
    rs = [q0*(mu/K + (1-mu)/q) for q in qs]
    r1, r2 = rs
    return (l*f0-r1)*(1-f0)/(r2-r1)

def f1_pis_eq_0_new(f0, qs, l, mu):
    K, q0 = qs[-1], 1.0
    rs = [q0*(mu/K + (1-mu)/q) for q in qs]
    r1, r2 = rs
    return (r2-l*f0)*(1-f0)/(r2-r1)


def f1_pi2_eq_0(f0, pi1, qs, l, mu):
    K, q0 = qs[-1], 1.0
    rs = [q0*(mu/K + (1-mu)/q) for q in qs]
    r1, r2 = rs
    return  (-l*f0**2 + f0*((1-l)*pi1+l+r2) - r2 )/(r1 - r2)

def f2_pi2_eq_0(f0, pi1, qs, l, mu):
    K, q0 = qs[-1], 1.0
    rs = [q0*(mu/K + (1-mu)/q) for q in qs]
    r1, r2 = rs
    return  (-l*f0**2 + f0*((1-l)*pi1+l+r1) - r1 )/(r2 - r1)


def main():
    args = parser.parse_args()
    pi1, pi2, q1, q2, l, mu = args.pi1, args.pi2, args.q1, args.q2, args.l, args.mu
    # print(f'mu = {mu}')
    qs, pis = [q1, q2], [pi1, pi2]
    if l == 0.0:
        f0 = f0_lambda_eq_0(pi1, pi2, q1, q2, l, mu)
        solution = (f0, f_i(1, f0, pis, qs, l, mu), f_i(2, f0, pis, qs, l, mu))
        if args.verbosity >= 2:
            print(f"Exact solution, pi1, pi2 = {pi1}, {pi2}; q1, q2 = {q1}, {q2}, lambda = {l}")
            print(solution)
        else:
            print(*solution)
    else:
        if pi1 > 0.0 and pi2 > 0.0:
            f0_roots_abs = f0_lambda_neq_0(pi1, pi2, q1, q2, l, mu)
            # f0_roots_abs = [round(f0,12) for f0 in f0_roots_abs]
            f1s = [f_i(1,f0, pis, qs, l, mu) for f0 in f0_roots_abs]
            f2s = [f_i(2,f0, pis, qs, l, mu) for f0 in f0_roots_abs]
        elif pi1 == 0.0 and pi2 == 0.0:
            # f0_roots_abs = f0_lambda_neq_0_pi_eq_0(q1, q2, l, mu)
            f0_roots_abs = f0_lambda_neq_0(pi1, pi2, q1, q2, l, mu)
            f2s = [f2_pis_eq_0_new(f0,qs,l,mu) for f0 in f0_roots_abs]
            f1s = [f1_pis_eq_0_new(f0,qs,l,mu) for f0 in f0_roots_abs]
        elif pi1 > 0.0 and pi2 == 0.0:
            f0_roots_abs = f0_lambda_neq_0(pi1, pi2, q1, q2, l, mu)
            f1s = [f1_pi2_eq_0(f0,pi1,qs,l,mu) for f0 in f0_roots_abs]
            f2s = [f2_pi2_eq_0(f0,pi1,qs,l,mu) for f0 in f0_roots_abs]
            # f1s = [1-f0-f2 for f0,f2 in zip(f0_roots_abs,f2s)]
        # print(f0_roots_abs)
        solutions = [(f0,f1,f2) for f0,f1,f2 in zip(f0_roots_abs,f1s,f2s)]
        if args.verbosity >= 2:
            print(f"All solutions from the polynomial; pi1, pi2 = {pi1}, {pi2}; q1, q2 = {q1}, {q2}, lambda = {l}")
            for sol in solutions:
                print(sol)
            for i,sol in enumerate(solutions):
                if all(f >= 0 for f in sol):
                    print(f'Valid solution when m = {i}')
                    print(sol)
        elif args.verbosity == 1:
            for sol in solutions:
                print(*sol)
        else:
            for i,sol in enumerate(solutions):
                if all(f >= 0 for f in sol) and isclose(sum(sol),1.0,atol=5e-5):
                    valid_sol = sol
            print(*valid_sol)

if __name__ == '__main__':
    main()


