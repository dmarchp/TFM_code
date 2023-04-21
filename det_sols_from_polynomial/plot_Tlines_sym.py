import pandas as pd
import numpy as np
import os
from scipy.stats import linregress
from subprocess import call
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    path = '/res_files'

def plot_Qlines(q2, q1s, x=2):
    colors = plt.cm.gnuplot(np.linspace(0,1,len(q1s)))
    fig, ax = plt.subplots(figsize=(5.6,4.8))
    for i,q1 in enumerate(q1s):
        tline = pd.read_csv(f'{path}/Tline_sym_pis_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
        ax.plot(tline['pi'], tline['lambda'], label=f'{q1}', color=colors[i])
    ax.set(xlabel='$\pi_{1,2}$', ylabel='$\lambda$', xlim=(0, 0.5), ylim=(0,1))
    fig.legend(title=f'$q_1, \; q_2 = {q2}$', fontsize=8, title_fontsize=9, loc=(0.2,0.74))
    fig.tight_layout()
    fig.savefig(f'tlines_sym_q2_{q2}_f2_{x}f1.png')


q_pairs_Delta = {
    0.053:[(9,10), (18,20), (27,30), (36,40)],
    0.111:[(8,10), (16,20), (24,30), (32,40)],
    0.176:[(7,10), (14,20), (21,30), (28,40)],
    0.250:[(6,10), (12,20), (18,30), (24,40)]}

def plot_Qlines_manyDelta(Deltas, x=2):
    fig, ax = plt.subplots(figsize=(5.6,4.8))
    colors = plt.cm.gist_rainbow(np.linspace(0,1,len(Deltas)))
    for Delta, color in zip(Deltas, colors):
        for i,q_pair in enumerate(q_pairs_Delta[Delta]):
            tline = pd.read_csv(f'{path}/Tline_sym_pis_q1_{q_pair[0]}_q2_{q_pair[1]}_f2_{int(x)}f1.csv')
            if i == len(q_pairs_Delta[Delta])-1:
                ax.plot(tline['pi'], tline['lambda'], color=color, label=f'{q_pairs_Delta[Delta][0]}', alpha=(i+1)/len(q_pairs_Delta[Delta]), lw=0.7)
            else:
                ax.plot(tline['pi'], tline['lambda'], color=color, alpha=(i+1)/len(q_pairs_Delta[Delta]), lw=0.7)
    ax.set(xlabel='$\pi_{1,2}$', ylabel='$\lambda$', xlim=(0,0.5), ylim=(0,1))
    fig.legend(fontsize=8, loc=(0.2,0.74))
    fig.tight_layout()
    fig.savefig(f'tlines_sym_manyDeltas_f2_{x}f1.png')

# old integer q's
# q1s_q2 = {
#     10: list(range(4,10)),
#     20: list(range(9,20)),
#     30: list(range(13,30)),
#     40: [18,19,20,21,22,23] + list(range(24,40,4)) + [37,38,39]
# }

q1s_q2 = {
    5.0:[i/10 for i in range(22,50,3)],
    7.0:[2.5, 2.8, 3.1, 3.4]+[i/10 for i in range(35,70,3)],
    10.0:[4.3,4.6,4.9]+[i/10 for i in range(50,100,3)], 
    20.0:[i/10 for i in range(90,200,5)],
    30.0:[i/10 for i in range(130, 300, 5)],
    40.0:[float(i) for i in range(18,23)]+[i/10 for i in range(240,400,5)]
}

def plot_lambda_threshold_delta(q2s, pi, x=2):
    fig, ax = plt.subplots(figsize=(5.6,4.8))
    colors = plt.cm.gist_rainbow(np.linspace(0,1,len(q2s)))
    for q2, color in zip(q2s, colors):
        deltas, lambdas = [], []
        for q1 in q1s_q2[q2]:
            if not os.path.exists(f'{path}/Tline_sym_pis_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_sym.py {q1} {q2} {x}', shell=True)
            tline = pd.read_csv(f'{path}/Tline_sym_pis_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
            lamb = float(tline.query('pi == @pi')['lambda'])
            if np.isnan(lamb):
                lambdas.append(0)
            else:
                lambdas.append(lamb)
            deltas.append((q2-q1)/(q2+q1))
        ax.plot(deltas, lambdas, label=f'{q2}', color=color, marker='.', lw=0.8, markersize=3)
    ax.axvline(0.3333, color='xkcd:gray', ls=':', lw=0.8)
    ax.set(xlabel='$\Delta$', ylabel='$\lambda_c$', xlim=(0), ylim=(-0.01))
    fig.legend(loc=(0.85, 0.75), fontsize=8, title='$q_2$', title_fontsize=9)
    fig.text(0.45, 0.97, f'$\pi_{{1,2}} = {pi}$, $Q = f_2 - {x}f1$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'lambda_threshold_f2_{x}f1_sym_pi_{pi}_Delta.png')

def powerLaw(x,a,b):
    return a*x+b

def plot_lambda_threshold_pis(q2, pis, x=2, linfit=False):
    fig, ax = plt.subplots(figsize=(5.6,4.8))
    colors = plt.cm.gnuplot(np.linspace(0,1,len(pis)))
    pimax = max(pis)
    for pi, color in zip(pis, colors):
        deltas, lambdas = [], []
        for q1 in q1s_q2[q2]:
            if not os.path.exists(f'{path}/Tline_sym_pis_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_sym.py {q1} {q2} {x}', shell=True)
            tline = pd.read_csv(f'{path}/Tline_sym_pis_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
            lamb = float(tline.query('pi == @pi')['lambda'])
            if np.isnan(lamb):
                lambdas.append(0)
            else:
                lambdas.append(lamb)
            deltas.append((q2-q1)/(q2+q1))
        ax.plot(deltas, lambdas, label=f'{pi}', color=color, marker='.', lw=0.8, markersize=3)
        if pi == pimax and linfit:
            deltas.reverse(), lambdas.reverse()
            first0index = lambdas.index(0)
            deltas = deltas[:first0index+1]
            lambdas = lambdas[:first0index+1]
            linfit = linregress(deltas, lambdas)
            m, n = linfit[0], linfit[1]
            fitted_lambdas = [m*delta+n for delta in deltas]
            ax.plot(deltas, fitted_lambdas, ls='--', color='k', lw=0.8)
            fig.text(0.6, 0.6, f'm = {round(m,3)}, n = {round(n,3)}', fontsize=8)
        if pi == pimax:
            deltas.reverse(), lambdas.reverse()
            first0index = lambdas.index(0)
            firstToLast = ([deltas[0], deltas[first0index]],[lambdas[0], lambdas[first0index]])
            ax.plot(firstToLast[0], firstToLast[1], ls='--', color='k', lw=0.8)
        # powerlaw fit to pi  = 0.1
        # if pi == 0.1:
        #     deltas.reverse(), lambdas.reverse()
        #     first0index = lambdas.index(0)
        #     deltas = deltas[:first0index-2]
        #     lambdas = lambdas[:first0index-2]
        #     params, pcov = curve_fit(powerLaw, deltas, lambdas)
        #     fit = powerLaw(np.array(deltas), *params)
        #     ax.plot(deltas, fit, color='k', ls='-.', lw=0.8)
        #     print(params)
    ax.axvline(0.3333, color='xkcd:gray', ls=':', lw=0.8)
    ax.set(xlabel='$\Delta$', ylabel='$\lambda_c$', xscale='log', yscale='log')
    fig.legend(loc=(0.7, 0.6), fontsize=8, title='$\pi_{1,2}$', title_fontsize=9)
    fig.text(0.45, 0.97, f'$\pi_{{1,2}} = {pi}$, $Q = f_2 - {x}f1$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'lambda_threshold_f2_{x}f1_sym_manyPi_Delta.png')
    



# plot_Qlines(10, [6,7,8,9])

# plot_Qlines_manyDelta([0.053, 0.111, 0.176, 0.250])

# plot_lambda_threshold_delta([5.0, 7.0, 10.0, 20.0, 30.0, 40.0], 0.05)

plot_lambda_threshold_pis(40.0, [0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5])

