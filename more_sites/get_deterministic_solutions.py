import os
import glob
from subprocess import call
import numpy as np
import pandas as pd
import argparse
import sys
sys.path.append('../')
from package_global_functions import *

def prepare_ic_int(Nsites, ic):
    if ic == 'N':
        fs0 = [1,]
        fs0.extend([0.0]*Nsites)
    elif ic == 'E':
        fs0 = [0.0,]
        fs0.extend([1/Nsites]*Nsites)
    elif ic == 'E0':
        fs0 = [1/(Nsites+1)]*Nsites
    return fs0

# EULER INTEGRATION FUNCTIONS:
def fs_evo_eq(fs,pis,qs,l):
    dfsdt = [0.0,]
    for i in range(len(fs)-1):
        site_i = i+1
        dfdt = fs[0]*((1-l)*pis[i]+l*fs[site_i]) - fs[site_i]/qs[i]
        dfsdt.append(dfdt)
    dfsdt[0] = -1*sum(dfsdt[1:])
    return dfsdt

def sols_from_intEvo(pis, qs, l, fs0, max_time=2000):
    fs = fs0
    dt = 1
    for _ in range(max_time):
        dfsdt = fs_evo_eq(fs,pis,qs,l)
        fs = [f+dfdt*dt for f,dfdt in zip(fs,dfsdt)]
        # print(dfsdt)
        # print(fs)
        # input('enter')
    return fs
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pis', help='pis, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('l', type=float, help='interdependence (lambda)')
    parser.add_argument('ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    args = parser.parse_args()
    pis, qs, l, ic = args.pis, args.qs, args.l, args.ic
    if len(pis) != len(qs):
        print('Input number of pis different from qualities. Aborting.')
        exit()
    Nsites = len(pis)
    # assign the initial condition
    fs0 = prepare_ic_int(Nsites, ic)
    check = False
    # check: print parameters
    if check == True:
        print('Geting the deterministic solutions with the following parameters:')
        print(f'pis: {pis}')
        print(f'qualities: {qs}')
        print(f'lambda: {l}')
        print(f'ic: {ic}, fs0 = {fs0}')
    fs = sols_from_intEvo(pis, qs, l, fs0)
    print(*fs)

if __name__ == '__main__':
    main()