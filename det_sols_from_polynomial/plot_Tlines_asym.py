# ASYMMETRIC PIS
# plot the theoretical lines in a white backround phase space pi1,pi2;
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os
from subprocess import call
from f0poly_sols_clean import f0_lambda_neq_0
import numpy as np
import sys
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    path = '/res_files'

# parser = argparse.ArgumentParser()
# parser.add_argument('q1', type=int, help='site 1 quality')
# parser.add_argument('q2', type=int, help='site 2 quality')
# parser.add_argument('x', type=float, help='factor between f1 and f2, f2 = x*f1')
# args = parser.parse_args()

# q1, q2, x = args.q1, args.q2, args.x

def latexFont(size= 15, labelsize=18, titlesize=20, ticklabelssize=15, legendsize = 18):
    plt.rcParams.update({
        "text.usetex": True})    
    plt.rcParams["text.latex.preamble"].join([
        r"\usepackage{underscore}"
    ])    
    plt.rcParams["font.family"] = 'STIXGeneral'

#latexFont()


####### Q lines in the usual state space (pi1, pi2) lambda constant ##########################
def plot_Qlines_pi1pi2_dif_lambda(ls, q1, q2, x=2, xlim=(0,0.5), ylim=(0,0.5)):
    # ls = [l/10 for l in range(10)]
    fig, ax = plt.subplots(figsize=(4.8,4.8))
    ax.set(xlabel=r'$\pi_1$', ylabel=r'$\pi_2$', xlim=xlim, ylim=ylim)
    colors = plt.cm.gnuplot(np.linspace(0,1,len(ls)))
    for i,l in enumerate(ls):
        tline = pd.read_csv(f'{path}/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
        ax.plot(tline['pi1'], tline['pi2'], lw=0.8, color=colors[i], label=f'{l}')
    fig.legend(title=r'$\lambda$', fontsize=8, title_fontsize=9, loc=(0.2, 0.55))
    ax.set_aspect(1.0)
    fig.text(0.4, 0.96, rf'$q_1 = {q1}, q_2 = {q2}$')
    fig.tight_layout()
    fig.savefig(f'Tlines_asym_pi1pi2_q1_{q1}_q2_{q2}_f2_{int(x)}f1.png')
    plt.close(fig)

def plot_Qlines_pi1pi2_dif_q1(q1s, q2, l, x=2, xlim=(0,0.5), ylim=(0,0.5)):
    fig, ax = plt.subplots(figsize=(4.8,4.8))
    colors = plt.cm.cool(np.linspace(0,1,len(q1s)))
    ax.set(xlabel=r'$\pi_1$', ylabel=r'$\pi_2$', xlim=xlim, ylim=ylim)
    for i,q1 in enumerate(q1s):
        tline = pd.read_csv(f'{path}/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
        ax.plot(tline['pi1'], tline['pi2'], lw=0.8, color=colors[i], label=f'{q1}')
    fig.legend(title=r'$q_1$', fontsize=8, title_fontsize=9, loc=(0.2, 0.3))
    ax.set_aspect(1.0)
    fig.text(0.4, 0.96, rf'$\lambda = {l}, q_2 = {q2}$')
    fig.tight_layout()
    fig.savefig(f'Tlines_asym_pi1pi2_l_{l}_q2_{q2}_f2_{int(x)}f1.png')
    plt.close(fig)
#############################################################################################

#### Q lines in ( lambda, pi2) representation #### unused
def plot_Qlines_lambda():
    ls = [l/10 for l in range(10)]
    pi1s = [0.2, 0.4, 0.6, 0.8]
    colors = plt.cm.gnuplot(np.linspace(0,1,len(pi1s)))
    pi2s_l = [[],[],[],[]]
    for l in ls:
        tline = pd.read_csv(f'{path}/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
        for i,pi1 in enumerate(pi1s):
            pi2 = tline.query('pi1 == @pi1')['pi2']
            pi2s_l[i].append(pi2)
    fig, ax = plt.subplots()
    for i,pi in enumerate(pi1s):
        ax.plot(ls, pi2s_l[i], label=f'{pi1}', color=colors[i])
    ax.set(xlabel='$\lambda$', ylabel='$\pi_2$')
    fig.text(0.4, 0.98, rf'$q_1 = {q1}, q_2 = {q2}$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'Tlines_asym_q1_{q1}_q2_{q2}_f2_{int(x)}f1_lambda.png')
    plt.close(fig)


####### Q lines in the state space (pi2, lambda), pi1 constant ###############################
def plot_Qlines_pi2lam_difq1(q1s, q2, pi1, x=2, xlim=(0,0.5), ylim=(0,1)):
    fig, ax = plt.subplots(figsize=(4.8,4.8))
    colors = plt.cm.cool(np.linspace(0,1,len(q1s)))
    ax.set(xlabel=r'$\pi_2$', ylabel=r'$\lambda$', xlim=xlim, ylim=ylim)
    for i,q1 in enumerate(q1s):
        if not os.path.exists(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv'):
            call(f'python find_Tlines_asym_fixPi1.py {q1} {q2} {pi1} {x}', shell=True)
        tline = pd.read_csv(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
        ax.plot(tline['pi2'], tline['lambda'], lw=0.8, color=colors[i], label=f'{q1}')
    fig.legend(title=r'$q_1$', fontsize=8, title_fontsize=9, loc=(0.7, 0.7))
    fig.text(0.4, 0.96, rf'$\pi_1= {pi1}, q_2 = {q2}$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'Tlines_asym_pi2lam_q2_{q2}_pi1_{pi1}_f2_{int(x)}f1.png')
    plt.close(fig)
##############################################################################################

q_pairs_Delta = {
    0.053:[(9,10), (18,20), (27,30), (36,40)],
    0.111:[(8,10), (16,20), (24,30), (32,40)],
    0.176:[(7,10), (14,20), (21,30), (28,40)],
    0.250:[(6,10), (12,20), (18,30), (24,40)],
    0.333:[(5,10), (10,20), (15,30), (20,40)],
    0.429:[(4,10), (8,20), (12,30), (16,40)],
    0.538:[(3,10), (6,20), (9,30), (12,40)],
    0.666:[(2,10), (4,20), (6,30), (8,40)],
    0.818:[(1,10), (2,20), (3,30), (4,40)]
}

def plot_Qlines_pi1pi2_dif_lambda_Delta(ls, Delta, x=2, xlim=(0,0.5), ylim=(0,0.5)):
    fig, ax = plt.subplots(figsize=(4.8,4.8))
    colors = plt.cm.gist_rainbow(np.linspace(0,1,len(ls)))
    ax.set(xlabel=r'$\pi_1$', ylabel=r'$\pi_2$', xlim=xlim, ylim=xlim)
    for l, color in zip(ls, colors):
        for i,q_pair in enumerate(q_pairs_Delta[Delta]):
            q1, q2, = q_pair
            if not os.path.exists(f'{path}/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_asym.py {q1} {q2} {l} {x}', shell=True)
            tline = pd.read_csv(f'{path}/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
            if i==len(q_pairs_Delta[Delta])-1:
                ax.plot(tline['pi1'], tline['pi2'], color=color, label=f'{l}', alpha=(i+1)/len(q_pairs_Delta[Delta]), lw=0.7)
            else:
                ax.plot(tline['pi1'], tline['pi2'], color=color, alpha=(i+1)/len(q_pairs_Delta[Delta]), lw=0.7)
    fig.legend(fontsize=8, loc=(0.2, 0.6))
    ax.set_aspect(1.0)
    q1, q2 = q_pairs_Delta[Delta][0][0], q_pairs_Delta[Delta][0][1]
    fig.text(0.4, 0.96, rf'$(q_1, q_2) = ({q1}, {q2})$')
    fig.tight_layout()
    fig.savefig(f'Tlines_asym_pi1pi2_q1_{q1}_q2_{q2}_Delta_f2_{int(x)}f1.png')
    plt.close(fig)

def plot_Qlines_pi1pi2_dif_q1_manyDelta(Deltas, l, x=2, xlim=(0,0.5), ylim=(0,0.5)):
    fig, ax = plt.subplots(figsize=(4.8,4.8))
    colors = plt.cm.gist_rainbow(np.linspace(0,1,len(Deltas)))
    ax.set(xlabel=r'$\pi_1$', ylabel=r'$\pi_2$', xlim=xlim, ylim=xlim)
    for Delta, color in zip(Deltas, colors):
        for i,q_pair in enumerate(q_pairs_Delta[Delta]):
            q1, q2 = q_pair
            if not os.path.exists(f'{path}/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_asym.py {q1} {q2} {l} {x}', shell=True)
            tline = pd.read_csv(f'{path}/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
            if i==len(q_pairs_Delta[Delta])-1:
                ax.plot(tline['pi1'], tline['pi2'], color=color, label=f'{q_pairs_Delta[Delta][0]}', alpha=(i+1)/len(q_pairs_Delta[Delta]), lw=0.7)
            else:
                ax.plot(tline['pi1'], tline['pi2'], color=color, alpha=(i+1)/len(q_pairs_Delta[Delta]), lw=0.7)
    fig.legend(fontsize=8, loc=(0.2, 0.6))
    ax.set_aspect(1.0)
    fig.text(0.4, 0.96, rf'$\lambda = {l}$')
    fig.tight_layout()
    fig.savefig(f'Tlines_asym_pi1pi2_l_{l}_manyDeltas_f2_{int(x)}f1.png')
    plt.close(fig)

def plot_Qlines_pi2lam_difq1_manyDelta(Deltas, pi1, x=2, xlim=(0,0.5), ylim=(0,1)):
    fig, ax = plt.subplots(figsize=(4.8,4.8))
    colors = plt.cm.gist_rainbow(np.linspace(0,1,len(Deltas)))
    ax.set(xlabel=r'$\pi_2$', ylabel=r'$\lambda$', xlim=xlim, ylim=ylim)
    for Delta, color in zip(Deltas, colors):
        for i,q_pair in enumerate(q_pairs_Delta[Delta]):
            q1, q2 = q_pair
            if not os.path.exists(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_asym_fixPi1.py {q1} {q2} {pi1} {x}', shell=True)
            tline = pd.read_csv(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
            if i==len(q_pairs_Delta[Delta])-1:
                ax.plot(tline['pi2'], tline['lambda'], color=color, label=f'{q_pairs_Delta[Delta][0]}', alpha=(i+1)/len(q_pairs_Delta[Delta]), lw=0.7)
            else:
                ax.plot(tline['pi2'], tline['lambda'], color=color, alpha=(i+1)/len(q_pairs_Delta[Delta]), lw=0.7)
    fig.legend(fontsize=8, loc=(0.7, 0.7))
    fig.text(0.4, 0.96, rf'$\pi_1= {pi1}$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'Tlines_asym_pi2lam_pi1_{pi1}_manyDeltas_f2_{int(x)}f1.png')
    plt.close(fig)


q1s_q2 = {
    5.0: [i/10 for i in range(4,50,3)],
    7.0: [i/10 for i in range(5,70,3)],
    10.0: [i/10 for i in range(10,100,3)],
    20.0: [i/10 for i in range(10,200,10)],
    30.0: [i/10 for i in range(30,300,10)],
    40.0: [float(q1) for q1 in list(range(1,40))]
}

def lambda_threshold_line(q1s, q2, pi1, pi2, x):
    deltas, lambdas, last_q1_l0 = [], [], False
    for q1 in q1s:
        if not os.path.exists(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv'):
            call(f'python find_Tlines_asym_fixPi1.py {q1} {q2} {pi1} {x}', shell=True)
        tline = pd.read_csv(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
        deltas.append((q2-q1)/(q2+q1))
        lamb = float(tline.query('pi2 == @pi2')['lambda'])
        if np.isnan(lamb):
            lambdas.append(0)
            last_q1_l0, qindex = q1, q1s_q2[q2].index(q1)
        else:
            lambdas.append(lamb)
    # extra q1s:
    if last_q1_l0:
        dq1 = q1s_q2[q2][1] - q1s_q2[q2][0]
        smaller_dq1 = dq1/10
        a, b, h = last_q1_l0+smaller_dq1, last_q1_l0+dq1-smaller_dq1, smaller_dq1
        extra_q1s = np.linspace(a, b, round((b-a)/h+1))
        extra_q1s = np.around(extra_q1s, 1)
        for q1 in extra_q1s:
            if not os.path.exists(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_asym_fixPi1.py {q1} {q2} {pi1} {x}', shell=True)
            tline = pd.read_csv(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
            deltas.insert(qindex+1, (q2-q1)/(q2+q1))
            lamb = float(tline.query('pi2 == @pi2')['lambda'])
            if np.isnan(lamb):
                lambdas.insert(qindex+1, 0)
            else:
                lambdas.insert(qindex+1, lamb)
            qindex += 1
    return deltas, lambdas

def plot_lambda_threshold_delta(q2s, pi1, pi2, x=2):
    fig, ax = plt.subplots(figsize=(5.6,4.8))
    colors = plt.cm.gist_rainbow(np.linspace(0,1,len(q2s)))
    for q2, color in zip(q2s, colors):
        deltas, lambdas = lambda_threshold_line(q1s_q2[q2], q2, pi1, pi2, x)
        ax.plot(deltas, lambdas, label=f'{q2}', color=color, marker='.', lw=0.8, markersize=3)
    ax.set(xlabel='$\Delta$', ylabel='$\lambda_c$')
    fig.legend(loc=(0.85, 0.75), fontsize=8)
    fig.text(0.45, 0.97, f'$\pi_1 = {pi1}, \; \pi_2 = {pi2}$, $Q = f_2 - {x}f1$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'lambda_threshold_f2_{x}f1_asym_pi1_{pi1}_pi2_{pi2}_Delta.png')


def plot_lambda_threshold_pi2s(pi2s, pi1, q2, x=2):
    fig, ax = plt.subplots(figsize=(5.6,4.8))
    colors = plt.cm.gnuplot(np.linspace(0,1,len(pi2s)))
    for pi2, color in zip(pi2s, colors):
        deltas, lambdas = lambda_threshold_line(q1s_q2[q2], q2, pi1, pi2, x)
        ax.plot(deltas, lambdas, label=f'{pi2}', color=color, marker='.', lw=0.8, markersize=2)
    ax.set(xlabel='$\Delta$', ylabel='$\lambda_c$')
    fig.legend(loc=(0.85, 0.75), fontsize=8, title_fontsize=9, title='$\pi_2$')
    fig.text(0.45, 0.97, f'$\pi_1 = {pi1}, \; q_2 = {q2}$, $Q = f_2 - {x}f1$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'lambda_threshold_f2_{x}f1_asym_pi1_{pi1}_manyPi2_oneDelta_q2_{q2}.png')


def plot_Delta_threshold_manyPi1(pi1s, q2, x=2, piFraction=True):
    """
    x ax can be either pi2 or pi2/(pi2+pi1) controlled by parameter piFraction
    """
    fig, ax = plt.subplots(figsize=(5.6,4.8))
    ax.set(ylabel='$\Delta_c$')
    colors = plt.cm.gnuplot(np.linspace(0,1,len(pi1s)))
    markers = ['.', '2', 'x', '+']
    markers = markers[:len(pi1s)]
    for pi1, color, marker in zip(pi1s, colors, markers):
        deltas_c = []
        #minpi2, maxpi2, spacing = 0.02, 0.5, 0.02
        minpi2, maxpi2, spacing = 0.02, 0.5, 0.01
        pi2s = np.linspace(minpi2, maxpi2, int((maxpi2-minpi2)/spacing)+1)
        pi2s = np.around(pi2s, 2)
        for pi2 in pi2s:
            deltas, lambdas = lambda_threshold_line(q1s_q2[q2], q2, pi1, pi2, x)
            deltas.reverse(), lambdas.reverse()
            deltas_c.append(deltas[lambdas.index(0)])
        if piFraction:
            pinorm = pi2s/(pi2s + pi1)
            ax.plot(pinorm, deltas_c, lw=0.8, marker=marker, color=color, label=f'{pi1}', markersize=5)
            ax.set_xlabel('$\pi_2 / (\pi_2 + \pi_1)$')
            figname = f'delta_threshold_f2_{x}f1_asym_manyPi1_xax_piFraction_q2_{q2}.png'
        else:
            ax.plot(pi2s, deltas_c, lw=0.8, marker=marker, color=color, label=f'{pi1}', markersize=5)
            ax.set_xlabel('$\pi_2$')
            figname = f'delta_threshold_f2_{x}f1_asym_manyPi1_xax_pi2_q2_{q2}.png'
    fig.text(0.4, 0.97, f'$Q = f_2 - {x} f_1$', fontsize=9)
    fig.legend(title='$\pi_1$', title_fontsize=9, fontsize=9, loc = (0.7, 0.75))
    fig.tight_layout()
    fig.savefig(figname)


# plot_Qlines_pi1pi2_dif_lambda([i/10 for i in range(5)], 3, 10, 2)
# plot_Qlines_pi1pi2_dif_lambda([i/10 for i in range(7)], 5, 10, 2)
# plot_Qlines_pi1pi2_dif_lambda([i/10 for i in range(8)], 7, 10, 2)
# plot_Qlines_pi1pi2_dif_lambda([i/10 for i in range(10)], 9, 10, 2)


# plot_Qlines_pi1pi2_dif_q1(list(range(1,10)), 10, 0.0)
# plot_Qlines_pi1pi2_dif_q1(list(range(2,10)), 10, 0.3)
# plot_Qlines_pi1pi2_dif_q1(list(range(5,10)), 10, 0.6)
# plot_Qlines_pi1pi2_dif_q1(list(range(9,10)), 10, 0.9)


# plot_Qlines_pi1pi2_dif_q1_manyDelta([0.053, 0.176, 0.333, 0.538], 0.0)
# plot_Qlines_pi1pi2_dif_q1_manyDelta([0.053, 0.176, 0.333, 0.538], 0.3)
# plot_Qlines_pi1pi2_dif_q1_manyDelta([0.053, 0.176, 0.333, 0.538], 0.6)
# plot_Qlines_pi1pi2_dif_q1_manyDelta([0.053, 0.176, 0.333, 0.538], 0.9)


# s'apren el mateix dels seguents plots que dels anteriors...
# plot_Qlines_pi1pi2_dif_lambda_Delta([0.0, 0.4, 0.8, 0.9], 0.053)
# plot_Qlines_pi1pi2_dif_lambda_Delta([0.0, 0.3, 0.5, 0.7], 0.176)
# plot_Qlines_pi1pi2_dif_lambda_Delta([0.0, 0.3, 0.5, 0.6], 0.333)
# plot_Qlines_pi1pi2_dif_lambda_Delta([0.0, 0.1, 0.2, 0.3], 0.666)


# canviem l'espai d'estats que mirem a (pi2, lambda):
# plot_Qlines_pi2lam_difq1([3,5,7,9], 10, 0.1)
# plot_Qlines_pi2lam_difq1([3,5,7,9], 10, 0.2)
# plot_Qlines_pi2lam_difq1([3,5,7,9], 10, 0.3)
# plot_Qlines_pi2lam_difq1([3,5,7,9], 10, 0.4)

# plot_Qlines_pi2lam_difq1_manyDelta([0.053, 0.176, 0.333, 0.538], 0.1)
# plot_Qlines_pi2lam_difq1_manyDelta([0.053, 0.176, 0.333, 0.538], 0.2)
# plot_Qlines_pi2lam_difq1_manyDelta([0.053, 0.176, 0.333, 0.538], 0.3)
# plot_Qlines_pi2lam_difq1_manyDelta([0.053, 0.176, 0.333, 0.538], 0.4)


# plot_lambda_threshold_delta([5.0,7.0,10.0,20.0,30.0,40.0], 0.4, 0.1, 2)
# plot_lambda_threshold_delta([5.0,7.0,10.0,20.0,30.0,40.0], 0.4, 0.2, 2)
# plot_lambda_threshold_delta([5.0,7.0,10.0,20.0,30.0,40.0], 0.4, 0.3, 2)

# plot_lambda_threshold_delta([5.0,7.0,10.0,20.0,30.0,40.0], 0.2, 0.05, 2)
# plot_lambda_threshold_delta([5.0,7.0,10.0,20.0,30.0,40.0], 0.2, 0.1, 2)
# plot_lambda_threshold_delta([5.0,7.0,10.0,20.0,30.0,40.0], 0.2, 0.15, 2)


# plot_lambda_threshold_pi2s([0.01, 0.03, 0.05, 0.10, 0.15, 0.19], 0.2, 40.0)
# plot_lambda_threshold_pi2s([0.05, 0.10, 0.15, 0.20, 0.22, 0.24, 0.26, 0.28], 0.3, 40.0)
# plot_lambda_threshold_pi2s([0.05, 0.10, 0.15, 0.2, 0.25, 0.35], 0.4, 40.0)

# plot_Delta_threshold_manyPi1([0.1, 0.2, 0.3, 0.4], 40.0, x = 1)
# plot_Delta_threshold_manyPi1([0.1, 0.2, 0.3, 0.4], 40.0)
# plot_Delta_threshold_manyPi1([0.1, 0.2, 0.3, 0.4], 40.0, x = 1, piFraction=False)
# plot_Delta_threshold_manyPi1([0.1, 0.2, 0.3, 0.4], 40.0, piFraction=False)
