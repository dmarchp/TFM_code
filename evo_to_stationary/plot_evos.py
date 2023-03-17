import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from subprocess import call
from functools import reduce
import sys
sys.path.append('../')
from package_global_functions import *


def get_avg_traj(dfs):
    df_avg = reduce(lambda a,b: a.add(b, fill_value=0), dfs)
    df_avg = df_avg/len(dfs)
    return df_avg

def getTimeEvosPath():
    extSSDpath = getExternalSSDpath()
    if os.path.exists(extSSDpath):
        path = extSSDpath + getProjectFoldername() + '/evo_to_stationary/time_evos_dif_cond'
    else:
        path = '/time_evos_dif_cond'
    return path

def plot_evos_dif_pis_sym(pis, q1, q2, l, N=500, statLine=False):
    fig, ax = plt.subplots()
    ax.set(xlabel='Iteration', ylabel='$f_2$', xscale='log')
    for pi in pis:
        # Nrea = len(glob.lgob(f'time_evos_dif_cond/time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q1}_q2_{q2}_l_{l}'))
        files = glob.glob(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q1}_q2_{q2}_l_{l}/*')
        dfs = [pd.read_csv(file) for file in files]
        df_avg = get_avg_traj(dfs)
        evoline, = ax.plot(df_avg['iter'], df_avg['f2'], alpha=0.8, label=f'{pi}', lw=0.7)
        if statLine:
            call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pi} {pi} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                ax.axhline(sols[2], color=evoline.get_color(), ls=':', lw=0.7)
    fig.legend(title='$\pi_{1,2}$', fontsize=8, title_fontsize=9, loc=(0.7, 0.2))
    fig.text(0.2, 0.8, f'$q_1 = {q1}, \; q_2 = {q2}, \; \lambda = {l}$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'time_evos_sym_pis_q1_{q1}_q2_{q2}_l_{l}_N_{N}.png')


def plot_evos_dif_q1s_sym(q1s, q2, pi, l, N=500, statLine=False):
    fig, ax = plt.subplots()
    ax.set(xlabel='Iteration', ylabel='$f_2$', xscale='log')
    for q1 in q1s:
        files = glob.glob(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q1}_q2_{q2}_l_{l}/*')
        dfs = [pd.read_csv(file) for file in files]
        df_avg = get_avg_traj(dfs)
        evoline, = ax.plot(df_avg['iter'], df_avg['f2'], alpha=0.8, label=f'{q1}', lw=0.7)
        if statLine:
            call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pi} {pi} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                ax.axhline(sols[2], color=evoline.get_color(), ls=':', lw=0.7)
    fig.legend(title='$q_1$', fontsize=8, title_fontsize=9, loc=(0.7, 0.2))
    fig.text(0.2, 0.8, f'$\pi_{{1,2}} = {pi}, \; q_2 = {q2}, \; \lambda = {l}$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'time_evos_sym_q1s_pi12_{pi}_q2_{q2}_l_{l}_N_{N}.png')


def plot_evos_dif_lambs_sym(lambs, pi, q1, q2, N=500, statLine=False):
    fig, ax = plt.subplots()
    ax.set(xlabel='Iteration', ylabel='$f_2$', xscale='log')
    for l in lambs:
        files = glob.glob(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q1}_q2_{q2}_l_{l}/*')
        dfs = [pd.read_csv(file) for file in files]
        df_avg = get_avg_traj(dfs)
        evoline, = ax.plot(df_avg['iter'], df_avg['f2'], alpha=0.8, label=f'{l}', lw=0.7)
        if statLine:
            call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pi} {pi} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                ax.axhline(sols[2], color=evoline.get_color(), ls=':', lw=0.7)
    fig.legend(title='$\lambda$', fontsize=8, title_fontsize=9, loc=(0.7, 0.2))
    fig.text(0.2, 0.8, f'$\pi_{{1,2}} = {pi}, \; q_1 = {q1}, \; q_2 = {q2}$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'time_evos_sym_lambs_pi12_{pi}_q1_{q1}_q2_{q2}_N_{N}.png')


# plot_evos_dif_pis_sym([0.1, 0.2, 0.3, 0.4], 7, 10, 0.3, statLine=True)

# plot_evos_dif_q1s_sym([3,5,7,9], 10, 0.3, 0.45, statLine=True)

plot_evos_dif_lambs_sym([0.0, 0.3, 0.6, 0.9], 0.1, 9, 10, statLine=True)