import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from subprocess import call
import sys
sys.path.append('../')
from package_global_functions import *

# global things
extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/stationary_distributions/data'
else:
    path = '/data'

fs_labels = {'f0':'$f_0$', 'f1':'$f_1$', 'f2':'$f_2$'}
fs_colors = {'f0':'xkcd:red', 'f1':'xkcd:green', 'f2':'xkcd:blue'}

def plot_histoPDF_fs(N, pi1, pi2, q1, q2, l):
    fig, ax = plt.subplots()
    ax.set(xlabel='$f_j$', ylabel='PDF')
    filename = path + f'/stat_data_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv'
    df = pd.read_csv(filename)
    # ax.hist([df['f0'], df['f1'], df['f2']], bins='auto', color=['xkcd:red', 'xkcd:green', 'xkcd:blue'])
    # ax.hist(df['f2'], bins='auto', density=True, histtype='bar', color='xkcd:blue')
    for f in zip(['f0', 'f1', 'f2']):
        _, bins, _ = ax.hist(df[f], density=True, rwidth=0.8, color=fs_colors[f], alpha=0.75, label=fs_labels[f])
        # binCenters = np.linspace(min(df[f]), max(df[f]), )
        # binLims = np.linspace(min(df[f]), max(df[f])+1)
        # binCenters, prob, dprob = hist1D(df[f], binLims, binCenters, isPDF = True)
    fig.legend(loc=(0.7, 0.75), fontsize=9)
    fig.text(0.25, 0.97, f'$N = {N}$, $(\pi_1, \pi_2) = ({pi1}, {pi2})$, $(q_1, q_2) = ({q1}, {q2})$, $\lambda = {l}$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'histoPDF_fs_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.png')


def plot_histoPDF_fi_difSystemSize(f, Ns, binsNs, pi1, pi2, q1, q2, l, detValue=False):
    """
    f = 'f0', 'f1', 'f2'
    """
    fig, ax = plt.subplots()
    ax.set(xlabel=fs_labels[f], ylabel='PDF')
    for N, b, i in zip(Ns, binsNs, range(len(Ns))):
        filename = path + f'/stat_data_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv'
        df = pd.read_csv(filename)
        ax.hist(df[f], bins=b, density=True, rwidth=0.8, alpha=0.6+i*0.15, label=N)
    if detValue:
        call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
        with open('sols.dat', 'r') as file:
            sols = [float(f) for f in file.readline().split()]
            ax.axvline(sols[int(f[1])], color='k', ls='-', lw=1.0)
    fig.legend(loc=(0.7, 0.75), fontsize=9, title='N', title_fontsize=9)
    fig.text(0.25, 0.97, f'$N = {N}$, $(\pi_1, \pi_2) = ({pi1}, {pi2})$, $(q_1, q_2) = ({q1}, {q2})$, $\lambda = {l}$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'histoPDF_{f}_Ns_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.png')


def replicaFiguraJulia():
    # https://stackoverflow.com/questions/27426668/row-titles-for-matplotlib-subplot
    fig = plt.figure(constrained_layout=True, figsize=(9.0, 4.80))
    subfigs = fig.subfigures(nrows=2, ncols=1, hspace=0.05)
    # fig, ax = plt.subplots(2,4, figsize=(8.40, 4.80))
    N = 35
    pi_pairs = ((0.3, 0.3), (0.4, 0.2))
    q1, q2 = 7, 10
    ls = [0.0, 0.3, 0.6, 0.9]
    for i, subfig in enumerate(subfigs): # rows
        pi1, pi2 = pi_pairs[i][0], pi_pairs[i][1]
        subfig.suptitle(f'$\pi_1 = {pi1}, \pi_2 = {pi2}$', fontsize=9)
        axs = subfig.subplots(nrows=1, ncols=4)
        for j, ax in enumerate(axs):
            l = ls[j]
            for f in ['f0', 'f1', 'f2']:
                filename = path + f'/stat_data_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv'
                df = pd.read_csv(filename)
                ax.hist(df[f], density=True, color=fs_colors[f], rwidth=0.8, alpha=0.75)
            if i == 0:
                ax.set_title(f'$\lambda = {l}$', fontsize=8)
            if i==1:
                ax.set_xlabel('$f_j$')
            if j==0:
                ax.set_ylabel('PDF')
    fig.savefig(f'fs_pis_sym_asym_multiplot_N_{N}_q1_{q1}_q2_{q2}.png')


# plot_histoPDF_fs(500, 0.1, 0.1, 7, 10, 0.6)

plot_histoPDF_fi_difSystemSize('f2', [5000, 500, 35], [10, 10, 18], 0.3, 0.3, 7, 10, 0.6, detValue=True)

# replicaFiguraJulia()
