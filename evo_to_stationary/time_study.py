import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import random
import time
from subprocess import call
from functools import reduce
import sys
sys.path.append('../')
from package_global_functions import *

random.seed(int(time.time()))

# same function as in plot_evos.py
def getTimeEvosPath():
    extSSDpath = getExternalSSDpath()
    if os.path.exists(extSSDpath):
        path = extSSDpath + getProjectFoldername() + '/evo_to_stationary/time_evos_dif_cond'
    else:
        path = '/time_evos_dif_cond'
    return path

def get_first_passage_times(qs: tuple, pis: tuple, l: float, N: int):
    q1, q2 = qs
    pi1, pi2 = pis
    # get the analytical solution
    call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
    with open('sols.dat', 'r') as file:
        sols = [float(f) for f in file.readline().split()]
        Q = sols[2]-2*sols[1]
    # get the dataframes with the time evolutions:
    folder = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
    files = glob.glob(f'{getTimeEvosPath()}/{folder}/*')
    dfs = [pd.read_csv(file) for file in files]
    # compare time evolutions to analytical sols to get first passage times:
    fp_times_f, fp_times_Q = [], []
    for df in dfs:
        # for this to work there must be no fluctuations bigger than the stationary value before reaching the stationary value
        # f2:
        df['f2_minusStat'] = df['f2'] - sols[2]
        dff = df.query('f2_minusStat > 0')
        fp_time_f = dff['iter'].iloc[0]
        fp_times_f.append(fp_time_f)
        # Q: 
        df['Q'] = df['f2'] - 2*df['f1']
        df['Q_minusStat'] = df['Q'] - Q
        if Q > 0:
            dfQ = df.query('Q_minusStat > 0')
        else:
            dfQ = df.query('Q_minusStat < 0')
        fp_time_Q = dfQ['iter'].iloc[0]
        fp_times_Q.append(fp_time_Q)
    return fp_times_f, fp_times_Q

def get_nth_passage_times(n, qs: tuple, pis: tuple, l: float, N: int):
    q1, q2 = qs
    pi1, pi2 = pis
    # get the analytical solution
    call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
    with open('sols.dat', 'r') as file:
        sols = [float(f) for f in file.readline().split()]
        Q = sols[2]-2*sols[1]
    # get the dataframes with the time evolutions:
    folder = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
    files = glob.glob(f'{getTimeEvosPath()}/{folder}/*')
    dfs = [pd.read_csv(file) for file in files]
    # compare time evolutions to analytical sols to get nth passage times:
    passage_times_f, passage_times_Q = [], []
    for i,df in enumerate(dfs):
        # for this to work there must be no fluctuations bigger than the stationary value before reaching the stationary value
        # f2:
        df['f2_minusStat'] = df['f2'] - sols[2]
        dff = df.query('f2_minusStat > 0')
        if len(dff) == 0:
            print(f'Trajectory {i} with pi1 = {pi1}, pi2 = {pi2}, q1 = {q1}, q2 = {q2}, l = {l}, does not have a passage time.')
            continue
        times = np.array(dff['iter'])
        passage_times_aux = [times[0], ]
        gaps = times[1:] - times[:-1]
        # gaps_gt_1 = gaps[gaps > 1]
        for i,g in enumerate(gaps):
            if g > 1:
                passage_times_aux.append(times[i])
                passage_times_aux.append(times[i+1])
            if len(passage_times_aux) >= n:
                break
        # select nth passage time:
        if len(passage_times_f) < n:
            print(f'Trajectory {i} with pi1 = {pi1}, pi2 = {pi2}, q1 = {q1}, q2 = {q2}, l = {l}, does not have a {n}th passage time.')
        passage_times_f.append(passage_times_aux[n-1])
        # Q:
        # not done yet
    return passage_times_f, passage_times_Q





# fpt = first passage time
def fpt_equal_qs_and_pis(qs: list, pis:list, l:float, N:int):
    fig, ax = plt.subplots(1,2, figsize=(9.8, 4.8))
    fpts_f_fixedpi, std_fpts_f_fixedpi = [[] for _ in range(len(pis))], [[] for _ in range(len(pis))]
    # jitterer_pis = sorted(np.random.normal(0.0, 0.025, len(qs)))
    # jitterer_qs = sorted(np.random.normal(0.0, 2.5, len(pis)))
    jitterer_pis = np.linspace(-0.01, 0.01, len(qs))
    jitterer_qs = np.linspace(-1,1, len(pis))
    for i,q in enumerate(qs):
        fpts_f_fixedq, std_fpts_f_fixedq = [], []
        for j,pi in enumerate(pis):
            #if not os.path.exists(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q}_q2_{q}_l_{l}'):
            #    call(f'python evo_to_stationary.py {pi} {pi} {q} {q} {l} {N} N {random.randint(0,10000000)}', shell=True)
            call(f'python evo_to_stationary.py {pi} {pi} {q} {q} {l} {N} N {random.randint(0,10000000)}', shell=True)
            fpts_f, fpts_Q = get_first_passage_times((q,q), (pi, pi), l , N)
            fpt_f, std_fpt_f = np.average(fpts_f), np.std(fpts_f)
            fpts_f_fixedq.append(fpt_f), std_fpts_f_fixedq.append(std_fpt_f)
            fpts_f_fixedpi[j].append(fpt_f), std_fpts_f_fixedpi[j].append(std_fpt_f)
        # ax[1].plot(pis, fpts_f_fixedq, label = f'{q}', marker='.', ls='-', lw=0.7)
        pis_jitter = np.array(pis) + jitterer_pis[i]
        ax[1].errorbar(pis_jitter, fpts_f_fixedq, std_fpts_f_fixedq, label=f'{q}', marker='.', ls='-', lw=0.7, capsize=3)
    for i,pi in enumerate(pis):
        # ax[0].plot(qs, fpts_f_fixedpi[i], label = f'{pi}', marker='.', ls='-', lw=0.7)
        qs_jitter = qs + jitterer_qs[i]
        ax[0].errorbar(qs_jitter, fpts_f_fixedpi[i], std_fpts_f_fixedpi[i], label=f'{pi}', marker='.', ls='-', lw=0.7, capsize=3)
    ax[0].set(xlabel='q', ylabel='FPT')
    ax[0].legend(title=f'$\pi$', fontsize=8, title_fontsize=8)
    ax[1].set(xlabel=r'$\pi$')
    ax[1].legend(title=r'$q$', fontsize=8, title_fontsize=8)
    fig.text(0.35, 0.97, rf'$\lambda = {l}$, $N = {N}$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'fpt_equal_qs_and_pis_l_{l}_N_{N}.png')

def nth_pt_equal_qs_and_pis(n, qs: list, pis:list, l:float, N:int):
    fig, ax = plt.subplots(1,2, figsize=(9.8, 4.8))
    npts_f_fixedpi, std_npts_f_fixedpi = [[] for _ in range(len(pis))], [[] for _ in range(len(pis))]
    jitterer_pis = np.linspace(-0.01, 0.01, len(qs))
    jitterer_qs = np.linspace(-1,1, len(pis))
    for i,q in enumerate(qs):
        npts_f_fixedq, std_npts_f_fixedq = [], []
        for j,pi in enumerate(pis):
            if not os.path.exists(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q}_q2_{q}_l_{l}'):
               call(f'python evo_to_stationary.py {pi} {pi} {q} {q} {l} {N} N {random.randint(0,10000000)}', shell=True)
            npts_f, npts_Q = get_nth_passage_times(n, (q,q), (pi, pi), l , N)
            npt_f, std_npt_f = np.average(npts_f), np.std(npts_f)
            npts_f_fixedq.append(npt_f), std_npts_f_fixedq.append(std_npt_f)
            npts_f_fixedpi[j].append(npt_f), std_npts_f_fixedpi[j].append(std_npt_f)
        # ax[1].plot(pis, fpts_f_fixedq, label = f'{q}', marker='.', ls='-', lw=0.7)
        pis_jitter = np.array(pis) + jitterer_pis[i]
        ax[1].errorbar(pis_jitter, npts_f_fixedq, std_npts_f_fixedq, label=f'{q}', marker='.', ls='-', lw=0.7, capsize=3)
    for i,pi in enumerate(pis):
        # ax[0].plot(qs, fpts_f_fixedpi[i], label = f'{pi}', marker='.', ls='-', lw=0.7)
        qs_jitter = qs + jitterer_qs[i]
        ax[0].errorbar(qs_jitter, npts_f_fixedpi[i], std_npts_f_fixedpi[i], label=f'{pi}', marker='.', ls='-', lw=0.7, capsize=3)
    ax[0].set(xlabel='q', ylabel=f'{n}th PT')
    ax[0].legend(title=f'$\pi$', fontsize=8, title_fontsize=8)
    ax[1].set(xlabel=r'$\pi$')
    ax[1].legend(title=r'$q$', fontsize=8, title_fontsize=8)
    fig.text(0.35, 0.97, rf'$\lambda = {l}$, $N = {N}$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'{n}th_pt_equal_qs_and_pis_l_{l}_N_{N}.png')

# plots, but can be modified to return the values of passage time to a bigger function that plots for different ls or different pi_pairs!!
def nth_pt_q_pairs(n, q_pairs, pi1, pi2, l, N, loglog=False):
    npts_q_pairs, std_npts_q_pairs = [], []
    deltas = []
    for q_pair in q_pairs:
        q1, q2 = q_pair
        deltas.append((q2-q1)/(q2+q1))
        if not os.path.exists(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'):
            call(f'python evo_to_stationary.py {pi1} {pi2} {q1} {q2} {l} {N} N {random.randint(0,10000000)}', shell=True)
        npts_f, npts_Q = get_nth_passage_times(n, (q1,q2), (pi1, pi2), l , N)
        npt_f, std_npt_f = np.average(npts_f), np.std(npts_f)
        npts_q_pairs.append(npt_f), std_npts_q_pairs.append(std_npt_f)
    fig, ax = plt.subplots()
    ax.set(xlabel=r'$\Delta$', ylabel=f'{n}th PT')
    if loglog:
        ax.set(xscale='log', yscale='log')
    ax.errorbar(deltas, npts_q_pairs, std_npts_q_pairs, marker='.', ls='-', lw=0.7, capsize=3)
    fig.text(0.3, 0.97, rf'$\lambda = {l}$, $N = {N}$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'q_pairs_q2_{q_pairs[0][1]}_{n}th_pt_l_{l}_N_{N}.png')

    



if __name__ == '__main__':
    # fpt_equal_qs_and_pis([10, 20, 30, 40], [0.1, 0.2, 0.3, 0.4], 0.6, 5000)
    # nth_pt_equal_qs_and_pis(2, [10, 20, 30, 40], [0.1, 0.2, 0.3, 0.4], 0.6, 5000)
    # nth_pt_equal_qs_and_pis(5, [10, 20, 30, 40], [0.1, 0.2, 0.3, 0.4], 0.6, 5000)
    # nth_pt_q_pairs(1, [(3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10)], 0.1, 0.1, 0.6, 5000)
    # nth_pt_q_pairs(5, [(3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10)], 0.1, 0.1, 0.6, 5000)
    # nth_pt_q_pairs(1, [(12,40), (16,40), (20,40), (24,40), (28,40), (32,40), (36,40)], 0.1, 0.1, 0.6, 5000)
    # nth_pt_q_pairs(5, [(12,40), (16,40), (20,40), (24,40), (28,40), (32,40), (36,40)], 0.1, 0.1, 0.6, 5000)
    nth_pt_q_pairs(1, [(12,40), (16,40), (20,40), (24,40), (28,40), (32,40), (36,40)], 0.1, 0.1, 0.9, 5000, loglog=True)


