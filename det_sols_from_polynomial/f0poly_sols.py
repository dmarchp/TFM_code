# DETERMINISTIC SOLUTIONS FROM THE f0 polynomial
import math, cmath

# model parameters:
l = 0.5
q1, q2 = 7, 10
r1, r2 = 1/q1, 1/q2
pi1, pi2 = 0.4, 0.2
qs, rs, pis = [q1, q2], [r1, r2], [pi1, pi2]

# a f0**3 + b f0**2 + c f0 + d = 0
a = -l**2
b = l**2 + l*(r1+r2) + l*(1-l)*(pi1+pi2)
c = -(1-l)*(pi1*r2 + pi2*r1) - l*(r1 + r2) - r1*r2
d = r1*r2

# solution:
delta0 = b**2 - 3*a*c
delta1 = 2*b**3 - 9*a*b*c + 27*a**2*d
# print('delta0', delta0)
# print('delta1', delta1)


# computation of C:
radicand0 = delta1**2 - 4*delta0**3
# print('radicand0', radicand0)
if radicand0 < 0:
    root0 = complex(0,math.sqrt(-1*radicand0))
else:
    root0 = complex(math.sqrt(radicand0),0)
# print('root0', root0)

radicand1 = (delta1 + root0)/2
# print('radicand1', radicand1)
C = radicand1**(1/3)
# print(C)

# ksi
ksi = complex(-1, math.sqrt(3))/2

# final solution:
if delta0 == 0.0 and delta1 == 0.0:
    delta0_over_C = 0
else:
    delta0_over_C = delta0/C

f0_roots, f0_roots_abs = [], []
for k in range(3):
    f0_root = -1/(3*a)*(b + ksi**k*C + delta0_over_C/ksi**k)
    f0_roots.append(f0_root), f0_roots_abs.append(abs(f0_root))

# print(f0_roots)
# print(f0_roots_abs)


def f_i(i,f0):
    global qs, rs, pis, l
    return (1-l)*pis[i-1]/(rs[i-1]/f0-l)

f1s = [f_i(1,f0) for f0 in f0_roots_abs]
f2s = [f_i(2,f0) for f0 in f0_roots_abs]
# print(f1s)
# print(f2s)

# sum_check = [f0+f1+f2 for f0,f1,f2 in zip(f0_roots_abs,f1s,f2s)]
# print(sum_check)

solutions = [(f0,f1,f2) for f0,f1,f2 in zip(f0_roots_abs,f1s,f2s)]

for sol in solutions:
    if all(f >= 0 for f in sol):
        print('Valid solution')
        print(sol)