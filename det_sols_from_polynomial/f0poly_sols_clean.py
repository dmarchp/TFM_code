import argparse
import math #, cmath

parser = argparse.ArgumentParser()

parser.add_argument('pi1', type=float, help='site 1 quality')
parser.add_argument('pi2', type=float, help='site 2 quality')
parser.add_argument('q1', type=int, help='site 1 quality')
parser.add_argument('q2', type=int, help='site 2 quality')
parser.add_argument('l', type=float, help='interdependence (lambda)')

parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")


# ------------ solution to the third degree poly, if lambda != 0.0 ----------
def f0_lambda_neq_0(pi1, pi2, q1, q2, l):
    r1, r2 = 1/q1, 1/q2
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

# ---------- exact solution to f0, when lambda == 0.0 --------------------------
def f0_lambda_eq_0(pi1, pi2, q1, q2, l):
    # global pi1, pi2, q1, q2, r1, r2, l
    return 1/(1+pi1*q1+pi2*q2)

# ----------------------- Rest of the populations ------------------------------
def f_i(i, f0, pis, qs, l):
    # global qs, rs, pis, l
    rs = [1/q for q in qs]
    return (1-l)*pis[i-1]/(rs[i-1]/f0-l)



def main():
    args = parser.parse_args()
    pi1, pi2, q1, q2, l = args.pi1, args.pi2, args.q1, args.q2, args.l
    qs, pis = [q1, q2], [pi1, pi2]
    if l == 0.0:
        f0 = f0_lambda_eq_0(pi1, pi2, q1, q2, l)
        solution = (f0, f_i(1, f0, pis, qs, l), f_i(2, f0, pis, qs, l))
        if args.verbose:
            print(f"Exact solution, pi1, pi2 = {pi1}, {pi2}; q1, q2 = {q1}, {q2}, lambda = {l}")
            print(solution)
        else:
            print(*solution)
    else:
        f0_roots_abs = f0_lambda_neq_0(pi1, pi2, q1, q2, l)
        # print(f0_roots_abs)
        f1s = [f_i(1,f0, pis, qs, l) for f0 in f0_roots_abs]
        f2s = [f_i(2,f0, pis, qs, l) for f0 in f0_roots_abs]
        solutions = [(f0,f1,f2) for f0,f1,f2 in zip(f0_roots_abs,f1s,f2s)]
        if args.verbose:
            print(f"All solutions from the polynomial; pi1, pi2 = {pi1}, {pi2}; q1, q2 = {q1}, {q2}, lambda = {l}")
            for sol in solutions:
                print(sol)
            for i,sol in enumerate(solutions):
                if all(f >= 0 for f in sol):
                    print(f'Valid solution when m = {i}')
                    print(sol)
        else:
            for i,sol in enumerate(solutions):
                if all(f >= 0 for f in sol):
                    valid_sol = sol
            print(*valid_sol)

if __name__ == '__main__':
    main()

