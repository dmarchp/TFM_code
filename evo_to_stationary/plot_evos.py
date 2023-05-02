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
    ax.set(xlabel='Iteration', ylabel='$f_2$', xscale='symlog', ylim=(0,1)) # xlim=(0,600)
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


def plot_evos_deriv(pi1, pi2, q1, q2, l, N, integrated=False):
    fig, ax = plt.subplots()
    ax.set(xlabel='Iteration', ylabel='$d \; f_2$', xscale='symlog', xlim=(0,600))
    folder = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
    files = glob.glob(f'{getTimeEvosPath()}/{folder}/*')
    dfs = [pd.read_csv(file) for file in files]
    for df in dfs:
        f2 = np.array(df['f2'])
        derf2 = np.zeros(f2.shape)
        derf2[0], derf2[1:-1], derf2[-1] = (f2[1] - f2[0]), (f2[2:] - f2[0:-2])/2, (f2[-1] - f2[-2])
        df['df2'] = derf2
        ax.plot(df['iter'], df['df2'], color='xkcd:gray', lw=0.8, alpha=0.8)
    if integrated:
        intEvoFile = f'/time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_Euler.csv'
        dfint = pd.read_csv(f'{getTimeEvosPath()}/{intEvoFile}')
        f2 = np.array(dfint['f2'])
        derf2 = np.zeros(f2.shape)
        derf2[0], derf2[1:-1], derf2[-1] = (f2[1] - f2[0]), (f2[2:] - f2[0:-2])/2, (f2[-1] - f2[-2])
        dfint['df2'] = derf2
        ax.plot(dfint['iter'], dfint['df2'], color='xkcd:black', lw=0.8)
    fig.text(0.2, 0.97, f'$(\pi_1 , \pi_2) = ({pi1}, {pi2}), \; (q_1 , q_2) = ({q1}, {q2}), \; \lambda = {l}$')
    fig.tight_layout()
    fig.savefig(f'time_evo_deriv_f2_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.png')
        


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
def test_pieron_law(q_pairs, pi1, pi2, l, N=500, statLine=True, normTime=False):
    fig, ax = plt.subplots(1,2, figsize=(9.8, 4.8))
    if normTime:
        ax[0].set(xlabel='Iteration / $q_2$', ylabel='$f_2$', xscale='log')
        ax[1].set(xlabel='Iteration / $q_2$', ylabel='$Q$', xscale='log')
    else:
        ax[0].set(xlabel='Iteration', ylabel='$f_2$', xscale='log')
        ax[1].set(xlabel='Iteration', ylabel='$Q$', xscale='log')
    iterLabel = 'iter_norm' if normTime else 'iter'
    for q_pair in q_pairs:
        q1, q2 = q_pair
        files = glob.glob(f'{getTimeEvosPath()}/time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}/*')
        dfs = [pd.read_csv(file) for file in files]
        df_avg = get_avg_traj(dfs)
        df_avg['Q'] = df_avg['f2'] - 2*df_avg['f1']
        df_avg['iter_norm'] = df_avg['iter']/q2
        fevoline, = ax[0].plot(df_avg[iterLabel], df_avg['f2'], alpha=0.8, label=f'({q1}, {q2})', lw=0.7)
        Qevoline, = ax[1].plot(df_avg[iterLabel], df_avg['Q'], alpha=0.8, label=f'({q1}, {q2})', lw=0.7)
        for df in dfs:
            df['iter_norm'] = df['iter']/q2
            ax[0].plot(df[iterLabel], df['f2'], alpha=0.3, lw=0.7, color=fevoline.get_color())
            df['Q'] = df['f2'] - 2*df['f1']
            ax[1].plot(df[iterLabel], df['Q'], alpha=0.3, lw=0.7, color=Qevoline.get_color())
        if statLine:
            call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                ax[0].axhline(sols[2], color=fevoline.get_color(), ls=':', lw=0.7)
                Q = sols[2]-2*sols[1]
                ax[1].axhline(Q, color=Qevoline.get_color(), ls=':', lw=0.7)
        # get first passage time:
        fp_times_f, fp_times_Q = [], []
        for df in dfs:
            df['f2_minusStat'] = df['f2'] - sols[2]
            df['Q_minusStat'] = df['Q'] - Q
            dff, dfQ = df.query('f2_minusStat > 0'), df.query('Q_minusStat > 0')
            fp_time_f, fp_time_Q = dff['iter'].iloc[0], dfQ['iter'].iloc[0]
            fp_times_f.append(fp_time_f/q2), fp_times_Q.append(fp_time_Q/q2)
        print(f'First passage norm times (f2) for $(q_1, q_2) = ({q1}, {q2})$: \n {fp_times_f}')
        print(f'Average first passage norm time (f2) for $(q_1, q_2) = ({q1}, {q2})$: {np.average(fp_times_f)} +- {np.std(fp_times_f)}')
        # print('----------------------------------------------------------------------------')
        print(f'First passage norm times (Q) for $(q_1, q_2) = ({q1}, {q2})$: \n {fp_times_Q}')
        print(f'Average first passage norm time (Q) for $(q_1, q_2) = ({q1}, {q2})$: {np.average(fp_times_Q)} +- {np.std(fp_times_Q)}')
        print('----------------------------------------------------------------------------')
    #fig.legend(title='$(q_1, q_2)$', fontsize=8, title_fontsize=9, loc=(0.7, 0.2))
    #fig.text(0.2, 0.8, f'$(\pi_1, \pi_2) = ({pi1}, {pi2}), \; q_1 = {q1}, \; q_2 = {q2}$', fontsize=8)
    ax[0].legend(title='$(q_1, q_2)$', fontsize=8, title_fontsize=8)
    ax[1].legend(title='$(q_1, q_2)$', fontsize=8, title_fontsize=8)
    fig.tight_layout()
    fig.savefig(f'time_evo_test_pieron_law_pi1_{pi1}_pi2_{pi2}_q1_{q_pairs[0][0]}_q2_{q_pairs[0][1]}_{iterLabel}.png')


# plot_evos_dif_pis_sym([0.1, 0.2, 0.3, 0.4], 7, 10, 0.3, statLine=True)

# plot_evos_dif_q1s_sym([3,5,7,9], 10, 0.3, 0.45, statLine=True)

# plot_evos_dif_lambs_sym([0.0, 0.3, 0.6, 0.9], 0.1, 9, 10, statLine=True)



# plot_evos_simple(0.4, 0.2, 7, 10, 0.6, 35, integrated=True, backg=0)
# plot_evos_simple(0.4, 0.2, 7, 10, 0.6, 35, ic='T', integrated=True, backg=0)
# plot_evos_simple(0.4, 0.2, 7, 10, 0.6, 35, ic='J', integrated=True, backg=1)
# plot_evos_simple(0.3, 0.3, 7, 10, 0.6, 35, ic='J', integrated=True, backg=1)

# test_pieron_law([(7,10), (28,40)], 0.1, 0.1, 0.6, 500)

# test_pieron_law([(10,10), (40,40)], 0.1, 0.1, 0.6, 500, normTime = True)
# test_pieron_law([(10,10), (40,40)], 0.4, 0.4, 0.6, 500, normTime = True)

# plot_evos_simple(0.1, 0.1, 10, 10, 0.6, 500, integrated=True, backg=5)

# plot_evos_deriv(0.1, 0.1, 7, 10, 0.6, 500, True)
# plot_evos_deriv(0.1, 0.1, 7, 10, 0.6, 5000, True)
plot_evos_simple(0.1, 0.1, 36, 40, 0.9, 5000, integrated=True, backg=5)