# ASYMMETRIC PIS
# plot the theoretical lines in a white backround phase space pi1,pi2;
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os
from subprocess import call
from f0poly_sols_clean import f0_lambda_neq_0
import numpy as np

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
        tline = pd.read_csv(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
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
        tline = pd.read_csv(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
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
        tline = pd.read_csv(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
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
        # if not os.path.exists(f'res_files/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv'):
        #     call(f'python find_Tlines_asym_fixPi1.py {q1} {q2} {pi1} {x}', shell=True)
        call(f'python find_Tlines_asym_fixPi1.py {q1} {q2} {pi1} {x}', shell=True)
        tline = pd.read_csv(f'res_files/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
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
            if not os.path.exists(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_asym.py {q1} {q2} {l} {x}', shell=True)
            tline = pd.read_csv(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
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
            if not os.path.exists(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_asym.py {q1} {q2} {l} {x}', shell=True)
            tline = pd.read_csv(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
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
            if not os.path.exists(f'res_files/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_asym_fixPi1.py {q1} {q2} {pi1} {x}', shell=True)
            tline = pd.read_csv(f'res_files/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
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
    10: list(range(1,10)),
    20: list(range(1,12)) + list(range(12,20,2)),
    30: list(range(1,12)) + list(range(12,30,4)),
    40: list(range(1,12)) + list(range(12,40,2))
}

def plot_lambda_threshold_delta(q2s, pi1, pi2, x=2):
    fig, ax = plt.subplots(figsize=(5.6,4.8))
    colors = plt.cm.gist_rainbow(np.linspace(0,1,len(q2s)))
    for q2, color in zip(q2s, colors):
        deltas, lambdas = [], []
        for q1 in q1s_q2[q2]:
            if not os.path.exists(f'res_files/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv'):
                call(f'python find_Tlines_asym_fixPi1.py {q1} {q2} {pi1} {x}', shell=True)
            tline = pd.read_csv(f'res_files/Tline_asym_fixPi1_pi1_{pi1}_q1_{q1}_q2_{q2}_f2_{int(x)}f1.csv')
            deltas.append((q2-q1)/(q2+q1))
            lamb = float(tline.query('pi2 == @pi2')['lambda'])
            if np.isnan(lamb):
                lambdas.append(0)
            else:
                lambdas.append(lamb)
        ax.plot(deltas, lambdas, label=f'{q2}', color=color, marker='.', lw=0.8, markersize=3)
    ax.set(xlabel='$\Delta$', ylabel='$\lambda_c$')
    fig.legend(loc=(0.85, 0.75), fontsize=8)
    fig.text(0.45, 0.97, f'$\pi_1 = {pi1}, \; \pi_2 = {pi2}$, $Q = f_2 - {x}f1$', fontsize=8)
    fig.tight_layout()
    fig.savefig(f'lambda_threshold_f2_{x}f1_asym_pi1_{pi1}_pi2_{pi2}_Delta.png')


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


# plot_lambda_threshold_delta([10,20,30,40], 0.4, 0.1, 2)
# plot_lambda_threshold_delta([10,20,30,40], 0.4, 0.2, 2)
# plot_lambda_threshold_delta([10,20,30,40], 0.4, 0.3, 2)

plot_lambda_threshold_delta([10,20,30,40], 0.2, 0.05, 2)
plot_lambda_threshold_delta([10,20,30,40], 0.2, 0.1, 2)
plot_lambda_threshold_delta([10,20,30,40], 0.2, 0.15, 2)