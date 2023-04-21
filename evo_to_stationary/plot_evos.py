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

def plot_evos_simple(pi1, pi2, q1, q2, l, N, ic = 'N', integrated=False, backg=False):
    """
    If backg != 0, plot the single (not averaged) trajectories in the background in a smooth fashion
    plots the amount indicated, eg backg = 5
    """
    fig, ax = plt.subplots()
    ax.set(xlabel='Iteration', ylabel='$f_2$', xscale='symlog', xlim=(0,600), ylim=(0,1))
    folder = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
    intEvoFile = f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
    figname = f'time_evo_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
    if ic == 'T':
        folder += '_ic_thirds'
        figname += '_ic_thirds'
        intEvoFile += '_ic_thirds'
    if ic == 'J':
        folder += '_ic_julia'
        figname += '_ic_julia'
        intEvoFile += '_ic_julia'
    intEvoFile += '_Euler.csv'
    figname += '.png'
    files = glob.glob(f'{getTimeEvosPath()}/{folder}/*')
    dfs = [pd.read_csv(file) for file in files]
    df_avg = get_avg_traj(dfs)
    if backg:
        for file in files[:backg]:
            df = pd.read_csv(file)
            ax.plot(df['iter'], df['f0'], alpha=0.2, lw=0.6, color='xkcd:red')
            ax.plot(df['iter'], df['f1'], alpha=0.2, lw=0.6, color='xkcd:green')
            ax.plot(df['iter'], df['f2'], alpha=0.2, lw=0.6, color='xkcd:blue')
    ax.plot(df_avg['iter'], df_avg['f0'], alpha=0.9, lw=0.7, label='$f_0$', color='xkcd:red')
    ax.plot(df_avg['iter'], df_avg['f1'], alpha=0.9, lw=0.7, label='$f_1$', color='xkcd:green')
    ax.plot(df_avg['iter'], df_avg['f2'], alpha=0.9, lw=0.7, label='$f_2$', color='xkcd:blue')
    if integrated:
        intEvo = pd.read_csv(f'{getTimeEvosPath()}/{intEvoFile}')
        for f in ['f0', 'f1', 'f2']:
            ax.plot(intEvo['iter'], intEvo[f], lw=0.7, ls='--', color='k')
    df_avg.to_csv(f'time_evo_avg_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv', index=False)
    ax.legend(fontsize=9)
    fig.text(0.2, 0.97, f'$(\pi_1 , \pi_2) = ({pi1}, {pi2}), \; (q_1 , q_2) = ({q1}, {q2}), \; \lambda = {l}$')
    fig.tight_layout() 
    fig.savefig(figname)



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


# test pieron's law:
def test_pieron_law(q_pairs, pi1, pi2, l, N=500, statLine=True):
    fig, ax = plt.subplots()
    ax.set(xlabel='Iteration / $q_2$', ylabel='$f_2$', xscale='log')
    for q_pair in q_pairs:
        q1, q2 = q_pair
        files = glob.glob(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}/*')
        dfs = [pd.read_csv(file) for file in files]
        df_avg = get_avg_traj(dfs)
        evoline, = ax.plot(df_avg['iter']/q2, df_avg['f2'], alpha=0.8, label=f'({q1}, {q2})', lw=0.7)
        for df in dfs:
            ax.plot(df['iter']/q2, df['f2'], alpha=0.4, lw=0.7, color=evoline.get_color())
        if statLine:
            call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                ax.axhline(sols[2], color=evoline.get_color(), ls=':', lw=0.7)
        # get first passage time:
        fp_times = []
        for df in dfs:
            df['f2_minusStat'] = df['f2'] - sols[2]
            df = df.query('f2_minusStat > 0')
            fp_time = df['iter'].iloc[0]
            fp_times.append(fp_time/q2)
        print(f'First passage norm times for $(q_1, q_2) = ({q1}, {q2})$: \n {fp_times}')
        print(f'Average first passage norm time for $(q_1, q_2) = ({q1}, {q2})$: {np.average(fp_times)} +- {np.std(fp_times)}')
    fig.legend(title='$(q_1, q_2)$', fontsize=8, title_fontsize=9, loc=(0.7, 0.2))
    fig.text(0.2, 0.8, f'$(\pi_1, \pi_2) = ({pi1}, {pi2}), \; q_1 = {q1}, \; q_2 = {q2}$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'time_evo_test_pieron_law.png')


# plot_evos_dif_pis_sym([0.1, 0.2, 0.3, 0.4], 7, 10, 0.3, statLine=True)

# plot_evos_dif_q1s_sym([3,5,7,9], 10, 0.3, 0.45, statLine=True)

# plot_evos_dif_lambs_sym([0.0, 0.3, 0.6, 0.9], 0.1, 9, 10, statLine=True)



# plot_evos_simple(0.4, 0.2, 7, 10, 0.6, 35, integrated=True, backg=0)
# plot_evos_simple(0.4, 0.2, 7, 10, 0.6, 35, ic='T', integrated=True, backg=0)
# plot_evos_simple(0.4, 0.2, 7, 10, 0.6, 35, ic='J', integrated=True, backg=1)
# plot_evos_simple(0.3, 0.3, 7, 10, 0.6, 35, ic='J', integrated=True, backg=1)

test_pieron_law([(7,10), (28,40)], 0.1, 0.1, 0.6, 500)