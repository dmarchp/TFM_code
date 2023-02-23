import numpy as np

def eigenVals_f1sol(r1,r2):
    radicand = r2**2 - 2*r2 + 1
    a = -r2 + 2*r1 -1
    ev1 = (a + np.sqrt(radicand))/2
    ev2 = (a - np.sqrt(radicand))/2
    return ev1, ev2

def eigenVals_f2sol(r1, r2):
    radicand = r1**2 - 2*r1 + 1
    a = -r1 + 2*r2 -1
    ev1 = (a + np.sqrt(radicand))/2
    ev2 = (a - np.sqrt(radicand))/2
    return ev1, ev2

q1, q2 = 29, 30
r1, r2 = 1/q1, 1/q2

ev1,ev2 = eigenVals_f1sol(r1,r2)
print(f'Eigenvalues f1 solution: {ev1}, {ev2}')
ev1,ev2 = eigenVals_f2sol(r1,r2)
print(f'Eigenvalues f2 solution: {ev1}, {ev2}')
