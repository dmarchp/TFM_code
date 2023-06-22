import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import random
import time
from subprocess import call
from functools import reduce
from scipy.optimize import curve_fit
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

def get_avg_traj(dfs):
    df_avg = reduce(lambda a,b: a.add(b, fill_value=0), dfs)
    df_avg = df_avg/len(dfs)
    return df_avg

def powerLaw(x, a, b):
    return a*x**b

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

def select_passage_time(n, df, i, pi1, pi2, q1, q2, l):
    times = np.array(df['iter'])
    passage_times_aux = [times[0], ]
    gaps = times[1:] - times[:-1]
    for j,g in enumerate(gaps):
        if g > 1:
            passage_times_aux.append(times[j])
            passage_times_aux.append(times[j+1])
        if len(passage_times_aux) >= n:
            break
    # select nth passage time:
    if len(passage_times_aux) < n:
        if i > 0:
            print(f'Trajectory {i} with pi1 = {pi1}, pi2 = {pi2}, q1 = {q1}, q2 = {q2}, l = {l}, does not have a {n}th passage time.')
        else:
            print(f'Average trajectory with pi1 = {pi1}, pi2 = {pi2}, q1 = {q1}, q2 = {q2}, l = {l}, does not have a {n}th passage time.')
        return 0
    else:
        # passage_times_f.append(passage_times_aux[n-1])
        return passage_times_aux[n-1]

def get_nth_passage_times(n, qs: tuple, pis: tuple, l: float, N: int, avgTraj=False):
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
            print(f'Trajectory {i} with pi1 = {pi1}, pi2 = {pi2}, q1 = {q1}, q2 = {q2}, l = {l}, does not have any passage time.')
            continue
        npt = select_passage_time(n, dff, i+1, pi1, pi2, q1, q2, l)
        if npt:
            passage_times_f.append(npt)
        # Q:
        # not done yet
    if avgTraj:
        dfavg = get_avg_traj(dfs)
        dfavg['f2_minusStat'] = dfavg['f2'] - sols[2]
        dffavg = dfavg.query('f2_minusStat > 0')
        if len(dffavg) == 0:
            print(f'Average Trajectory with pi1 = {pi1}, pi2 = {pi2}, q1 = {q1}, q2 = {q2}, l = {l}, does not have any passage time.')
        npt = select_passage_time(n, dffavg, 0, pi1, pi2, q1, q2, l)
        if npt:
            passage_time_avgTraj_f = npt
        return passage_times_f, passage_times_Q, passage_time_avgTraj_f
    else:
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
            if not os.path.exists(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q}_q2_{q}_l_{l}'):
               call(f'python evo_to_stationary.py {pi} {pi} {q} {q} {l} {N} N {random.randint(0,10000000)}', shell=True)
            # call(f'python evo_to_stationary.py {pi} {pi} {q} {q} {l} {N} N {random.randint(0,10000000)}', shell=True)
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

def nth_pt_equal_qs_and_pis(n, qs: list, pis:list, l:float, N:int, normPT = False):
    fig, ax = plt.subplots(1,2, figsize=(9.8, 4.8))
    npts_f_fixedpi, std_npts_f_fixedpi = [[] for _ in range(len(pis))], [[] for _ in range(len(pis))]
    jitterer_pis = np.linspace(-0.01, 0.01, len(qs))
    jitterer_qs = np.linspace(-1,1, len(pis))
    for i,q in enumerate(qs):
        npts_f_fixedq, std_npts_f_fixedq = [], []
        for j,pi in enumerate(pis):
            if not os.path.exists(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q}_q2_{q}_l_{l}'):
               call(f'python evo_to_stationary.py {pi} {pi} {q} {q} {l} {N} N {random.randint(0,10000000)}', shell=True)
            # call(f'python evo_to_stationary.py {pi} {pi} {q} {q} {l} {N} N {random.randint(0,10000000)}', shell=True)
            npts_f, npts_Q = get_nth_passage_times(n, (q,q), (pi, pi), l , N)
            if len(npts_f) > 1:
                npt_f, std_npt_f = np.average(npts_f), np.std(npts_f)
            elif len(npts_f) == 1:
                npt_f, std_npt_f = npts_f[0], 0.0
            elif len(npts_f) == 0:
                npt_f, std_npt_f = float('nan'), 0.0
            npts_f_fixedq.append(npt_f), std_npts_f_fixedq.append(std_npt_f)
            npts_f_fixedpi[j].append(npt_f), std_npts_f_fixedpi[j].append(std_npt_f)
        # ax[1].plot(pis, fpts_f_fixedq, label = f'{q}', marker='.', ls='-', lw=0.7)
        pis_jitter = np.array(pis) + jitterer_pis[i]
        if normPT:
            npts_f_fixedq, std_npts_f_fixedq = np.array(npts_f_fixedq)/q, np.array(std_npts_f_fixedq)/q
        ax[1].errorbar(pis_jitter, npts_f_fixedq, std_npts_f_fixedq, label=f'{q}', marker='.', ls='-', lw=0.7, capsize=3)
    for i,pi in enumerate(pis):
        # ax[0].plot(qs, fpts_f_fixedpi[i], label = f'{pi}', marker='.', ls='-', lw=0.7)
        qs_jitter = qs + jitterer_qs[i]
        if normPT:
            npts_f_fixedpi[i], std_npts_f_fixedpi[i] = [t/q for t,q in zip(npts_f_fixedpi[i], qs)], [t/q for t,q in zip(std_npts_f_fixedpi[i], qs)]
        ax[0].errorbar(qs_jitter, npts_f_fixedpi[i], std_npts_f_fixedpi[i], label=f'{pi}', marker='.', ls='-', lw=0.7, capsize=3)
    ax[0].set(xlabel='q', ylabel=f'{n}th PT')
    if normPT:
        ax[0].set(ylabel=f'{n}th PT / q')
    ax[0].legend(title=f'$\pi$', fontsize=8, title_fontsize=8)
    ax[1].set(xlabel=r'$\pi$')
    ax[1].legend(title=r'$q$', fontsize=8, title_fontsize=8)
    fig.text(0.35, 0.97, rf'$\lambda = {l}$, $N = {N}$', fontsize=9)
    fig.tight_layout()
    if normPT:
        fig.savefig(f'{n}th_normpt_equal_qs_and_pis_l_{l}_N_{N}.png')
    else:
        fig.savefig(f'{n}th_pt_equal_qs_and_pis_l_{l}_N_{N}.png')



# plots, but can be modified to return the values of passage time to a bigger function that plots for different ls or different pi_pairs!!
# nice but not pieron's law (?)
def nth_pt_q_pairs(n, q_pairs, pi1, pi2, l, N, loglog=False, powerLawFit=False, avgTraj=False):
    npts_q_pairs, std_npts_q_pairs, npts_avgTraj_q_pairs = [], [], []
    deltas, deltas2, q2s = [], [], []
    for q_pair in q_pairs:
        q1, q2 = q_pair
        deltas.append((q2-q1)/(q2+q1)), deltas2.append((q2-q1)/q2), q2s.append(q2)
        # deltas.append(q2-q1) # can't fit a powerlaw...
        if not os.path.exists(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'):
            call(f'python evo_to_stationary.py {pi1} {pi2} {q1} {q2} {l} {N} N {random.randint(0,10000000)}', shell=True)
        npts_f, npts_Q, npt_f_avgTraj = get_nth_passage_times(n, (q1,q2), (pi1, pi2), l , N, avgTraj = True)
        npt_f, std_npt_f = np.average(npts_f), np.std(npts_f)
        npts_q_pairs.append(npt_f), std_npts_q_pairs.append(std_npt_f), npts_avgTraj_q_pairs.append(npt_f_avgTraj)
    fig, ax = plt.subplots()
    ax.set(xlabel=r'$\Delta$', ylabel=f'{n}th PT')
    if loglog:
        ax.set(xscale='log', yscale='log')
    if avgTraj:
        passage_times = npts_avgTraj_q_pairs
    else:
        passage_times = npts_q_pairs
    xax = deltas2
    if powerLawFit:
        paramfit, covfit = curve_fit(powerLaw, xax, passage_times)
        fit = powerLaw(xax, *paramfit)
        ax.plot(xax, fit, ls='-.', lw=0.7, marker='None', color='r')
        ax.text(0.70, 0.65, f'a = {round(paramfit[0],5)}+-{round(np.sqrt(covfit[0,0]),5)}', fontsize=9, color='r', transform=ax.transAxes)
        ax.text(0.70, 0.60, f'b = {round(paramfit[1],5)}+-{round(np.sqrt(covfit[1,1]),5)}', fontsize=9, color='r', transform=ax.transAxes)
    if avgTraj:
        ax.plot(xax, passage_times, marker='.', ls='-', lw=0.7)
    else:
        ax.errorbar(xax, npts_q_pairs, std_npts_q_pairs, marker='.', ls='-', lw=0.7, capsize=3)
    fig.text(0.3, 0.97, rf'$(\pi_1, \pi_2) = ({pi1}, {pi2})$, $\lambda = {l}$, $N = {N}$', fontsize=9)
    fig.tight_layout()
    figname = f'q_pairs_q2_{q_pairs[0][1]}_{n}th_pt_pi1_{pi1}_pi2_{pi2}_l_{l}_N_{N}'
    if loglog:
        figname += '_loglog'
    if avgTraj:
        figname += '_avgTraj'
    figname += '.png'
    fig.savefig(figname)


def nth_pt_Delta_difPi(n, q_pairs, pis, l, N, normPT = False):
    q2s = [q_pair[1] for q_pair in q_pairs]
    jitterer_qs = np.linspace(-1,1, len(pis))
    fig, ax = plt.subplots()
    for i,pi in enumerate(pis):
        npts_fixPi, std_npts_fixPi = [], []
        for q_pair in q_pairs:
            q1, q2 = q_pair
            if not os.path.exists(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q1}_q2_{q2}_l_{l}'):
                call(f'python evo_to_stationary.py {pi} {pi} {q1} {q2} {l} {N} N {random.randint(0,10000000)}', shell=True)
            npts_f, npts_Q = get_nth_passage_times(n, (q1,q2), (pi, pi), l , N)
            npt_f, std_npt_f = np.average(npts_f), np.std(npts_f)
            if normPT:
                npts_fixPi.append(npt_f/q2), std_npts_fixPi.append(std_npt_f/q2)
            else:
                npts_fixPi.append(npt_f), std_npts_fixPi.append(std_npt_f)
        q2s_jitter = np.array(q2s) + jitterer_qs[i]
        ax.errorbar(q2s_jitter, npts_fixPi, std_npts_fixPi, marker='.', ls='-', lw=0.7, capsize=3, label=f'{pi}')
    # ax.set(xlabel=r'$q_2$', ylabel=f'{n}th PT')
    ax.set(xlabel=r'$q_2$')
    if normPT:
        ax.set_ylabel(f'{n}th PT / $q_2$')
    else:
        ax.set_ylabel(f'{n}th PT')
    fig.legend(title=r'$\pi_{1,2}$', fontsize=8, title_fontsize=8)
    delta = (q2 - q1)/(q2 + q1)
    fig.text(0.3, 0.97, rf'$\lambda = {l}$, $N = {N}$, $\Delta = {round(delta,3)}$, $(q_1, q_2) = ({q_pairs[0][0]}, {q_pairs[0][1]})...$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'delta_{q_pairs[0][0]}_{q_pairs[0][1]}_difPi_{n}th_pt_l_{l}_N_{N}.png')


def expo(x,a,b,c):
    return a*np.exp(b*x)+c

def decay(x,a,b):
    return a/x**b

def relaxation_time(pi1, pi2, q1, q2, l):
    intEvoFile = f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_Euler.csv'
    intEvo = pd.read_csv(f'{getTimeEvosPath()}/{intEvoFile}')
    # get the analytical solution
    # call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
    # with open('sols.dat', 'r') as file:
        # sols = [float(f) for f in file.readline().split()]
        # Q = sols[2]-2*sols[1]
    # use the last point of the integration as the solution (it is, actually)
    sols = [intEvo.iloc[-1][f'f{i}'] for i in range(3)]
    intEvo['f2_minusStat'] = sols[2] - intEvo['f2']
    
    fig, ax = plt.subplots()
    # ax.plot(intEvo['iter'], intEvo['f2_minusStat'], lw=0.8)
    # fit:
    time, data = np.array(intEvo['iter'])[10:400], np.array(intEvo['f2_minusStat'])[10:400]
    # paramfit, covfit = curve_fit(expo,time,data)
    # fit = expo(time, *paramfit)
    paramfit, curvedit = curve_fit(decay, time, data)
    fit = decay(time, *paramfit)
    ax.plot(time, data)
    ax.plot(time, fit, ls='-.', color='r', lw=0.8)
    # fig.text(0.45, 0.6, f'{round(paramfit[0],3)} e**({round(paramfit[1],3)} * t)', fontsize=9)
    fig.text(0.45, 0.6, f'{round(paramfit[0],3)} / (t ** {round(paramfit[1],3)})', fontsize=9)
    ax.set(xlabel='iteration', ylabel=r'$f_2^{*} - f_2$', xlim=(10,400))
    fig.tight_layout()
    fig.savefig(f'relaxation_f2_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.png')


def pierons_law_nth_pt_q_pairs_weber_frac(n, q_pairs, pi1, pi2, l, N, loglog=False, powerLawFit=False, avgTraj=False):
    '''
    q pairs with equal Weber Fraction. Time as a function of q2.
    '''
    npts_q_pairs, std_npts_q_pairs, npts_avgTraj_q_pairs = [], [], []
    wbfrac = (q_pairs[0][1] - q_pairs[0][0])/q_pairs[0][1]
    q2s = []
    for q_pair in q_pairs:
        q1, q2 = q_pair
        q2s.append(q2)
        if not os.path.exists(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'):
            call(f'python evo_to_stationary.py {pi1} {pi2} {q1} {q2} {l} {N} N {random.randint(0,10000000)}', shell=True)
        npts_f, npts_Q, npt_f_avgTraj = get_nth_passage_times(n, (q1,q2), (pi1, pi2), l , N, avgTraj = True)
        npt_f, std_npt_f = np.average(npts_f), np.std(npts_f)
        npts_q_pairs.append(npt_f), std_npts_q_pairs.append(std_npt_f), npts_avgTraj_q_pairs.append(npt_f_avgTraj)
    fig, ax = plt.subplots()
    ax.set(xlabel=r'$\Delta$', ylabel=f'{n}th PT')
    if loglog:
        ax.set(xscale='log', yscale='log')
    if avgTraj:
        passage_times = npts_avgTraj_q_pairs
    else:
        passage_times = npts_q_pairs
    xax = q2s
    if powerLawFit:
        paramfit, covfit = curve_fit(powerLaw, xax, passage_times)
        fit = powerLaw(xax, *paramfit)
        ax.plot(xax, fit, ls='-.', lw=0.7, marker='None', color='r')
        ax.text(0.70, 0.65, f'a = {round(paramfit[0],5)}+-{round(np.sqrt(covfit[0,0]),5)}', fontsize=9, color='r', transform=ax.transAxes)
        ax.text(0.70, 0.60, f'b = {round(paramfit[1],5)}+-{round(np.sqrt(covfit[1,1]),5)}', fontsize=9, color='r', transform=ax.transAxes)
    if avgTraj:
        ax.plot(xax, passage_times, marker='.', ls='-', lw=0.7)
    else:
        ax.errorbar(xax, npts_q_pairs, std_npts_q_pairs, marker='.', ls='-', lw=0.7, capsize=3)
    fig.text(0.3, 0.97, rf'$(\pi_1, \pi_2) = ({pi1}, {pi2})$, $\lambda = {l}$, $N = {N}$, $\Delta = {wbfrac}$', fontsize=9)
    fig.tight_layout()
    figname = f'q_pairs_Delta_{q_pairs[0][0]}_{q_pairs[0][1]}_{n}th_pt_pi1_{pi1}_pi2_{pi2}_l_{l}_N_{N}'
    if loglog:
        figname += '_loglog'
    if avgTraj:
        figname += '_avgTraj'
    figname += '.png'
    fig.savefig(figname)


def stat_time_from_block_avg(t, w, N, pi1, pi2, q1, q2, l):
    '''
    t: derivative threshold
    w: block size
    '''
    # get the dataframes with the time evolutions:
    folder = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
    files = glob.glob(f'{getTimeEvosPath()}/{folder}/*')
    dfs = [pd.read_csv(file) for file in files]
    for df in dfs:
        block_avgs = []
        # testing implementation in jupyter notebook!



if __name__ == '__main__':
    # nth_pt_equal_qs_and_pis(1, [10, 20, 30, 40], [0.1, 0.2, 0.3, 0.4], 0.6, 5000, normPT = True)
    # nth_pt_equal_qs_and_pis(1, [10, 20, 30, 40], [0.1, 0.2, 0.3, 0.4], 0.9, 5000, normPT = True)

    # nth_pt_q_pairs(1, [(3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10)], 0.1, 0.1, 0.6, 5000, loglog=True)
    # nth_pt_q_pairs(1, [(3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10)], 0.1, 0.1, 0.9, 5000, loglog=True, powerLawFit=True)
    # nth_pt_q_pairs(1, [(3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10)], 0.1, 0.1, 0.99, 5000, loglog=True, powerLawFit=True)
    # nth_pt_q_pairs(1, [(3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10)], 0.1, 0.1, 0.999, 5000, loglog=True, powerLawFit=True)
    

    # nth_pt_q_pairs(1, [(12,40), (16,40), (20,40), (24,40), (28,40), (32,40), (36,40)], 0.1, 0.1, 0.6, 5000, loglog=True, avgTraj=True)
    # nth_pt_q_pairs(1, [(12,40), (16,40), (20,40), (24,40), (28,40), (32,40), (36,40)], 0.1, 0.1, 0.9, 5000, loglog=True, powerLawFit=True)
    # nth_pt_q_pairs(1, [(12,40), (16,40), (20,40), (24,40), (28,40), (32,40), (36,40)], 0.1, 0.1, 0.99, 5000, loglog=True, powerLawFit=True)
    # nth_pt_q_pairs(1, [(12,40), (16,40), (20,40), (24,40), (28,40), (32,40), (36,40)], 0.1, 0.1, 0.999, 5000, loglog=True, powerLawFit=True)
    # nth_pt_Delta_difPi(5, [(7,10), (14,20), (21,30), (28,40)], [0.1, 0.2, 0.3, 0.4], 0.9, 5000, normPT=True)
    # nth_pt_Delta_difPi(1, [(9,10), (18,20), (27,30), (36,40)], [0.1, 0.2, 0.3, 0.4], 0.9, 5000, normPT=True)
    # relaxation_time(0.1, 0.1, 9, 10, 0.9)
    pierons_law_nth_pt_q_pairs_weber_frac(1, [(9,10), (18,20), (27,30), (36,40)], 0.1, 0.1, 0.9, 5000, True, True)


