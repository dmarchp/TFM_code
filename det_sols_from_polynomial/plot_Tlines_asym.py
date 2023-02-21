# ASYMMETRIC PIS
# plot the theoretical lines in a white backround phase space;
import matplotlib.pyplot as plt
import pandas as pd
import argparse
from f0poly_sols_clean import f0_lambda_neq_0
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('q1', type=int, help='site 1 quality')
parser.add_argument('q2', type=int, help='site 2 quality')
parser.add_argument('x', type=float, help='factor between f1 and f2, f2 = x*f1')
args = parser.parse_args()

q1, q2, x = args.q1, args.q2, args.x

def latexFont(size= 15, labelsize=18, titlesize=20, ticklabelssize=15, legendsize = 18):
    plt.rcParams.update({
        "text.usetex": True})    
    plt.rcParams["text.latex.preamble"].join([
        r"\usepackage{underscore}"
    ])    
    plt.rcParams["font.family"] = 'STIXGeneral'

#latexFont()


ls = [l/10 for l in range(10)]
colors = plt.cm.gnuplot(np.linspace(0,1,len(ls)))

fig, ax = plt.subplots(figsize=(4.8,4.8)) # 
ax.set(xlabel=r'$\pi_1$', ylabel=r'$\pi_2$', xlim=(0,1), ylim=(0,1))
for i,l in enumerate(ls):
    tline = pd.read_csv(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
    ax.plot(tline['pi1'], tline['pi2'], lw=0.8, color=colors[i], label=f'{l}')
    # if l%2 == 0:
    #     ax.text(tline['pi1'].iloc[-10], tline['pi2'].iloc[-10], f'$\lambda = {l}$')
fig.legend(title=r'$\lambda$', fontsize=8, loc=(0.2, 0.35))
ax.set_aspect(1.0)
fig.text(0.4, 0.96, rf'$q_1 = {q1}, q_2 = {q2}$')
fig.tight_layout()
fig.savefig(f'Tlines_asym_q1_{q1}_q2_{q2}_f2_{int(x)}f1.png')
plt.close(fig)


# anem a comprovar una cosa de la formula teorica de pi2:

# l = 0.1
# tline = pd.read_csv(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
# f0s, f0lq2, f0lq1 = [], [], []
# for row in tline.iterrows():
#     pi1, pi2 = row[1]['pi1'], row[1]['pi2']
#     _, f0, _ = f0_lambda_neq_0(pi1, pi2, q1, q2, l)
#     f0s.append(f0), f0lq2.append(f0*l*q2), f0lq1.append(f0*l*q1)


# f0lq2, f0lq1 = np.array(f0lq2), np.array(f0lq1)
# div = (1-f0lq2)/(1-f0lq1)
# print(div)



# T lines as a function of lambda; fixed pi1 (pi2 whatever)
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


# prova equacio
def aprox_pi2(pi1,q1,q2,l):
    l0 = pi1*q1/q2
    l0 = l0 * (1-l*q2)/(1-l*q1)
    
l = 0.4
tline = pd.read_csv(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
tline['aprox_pi2'] = tline.apply(lambda x: aprox_pi2(tline['pi1'], q1, q2, l)
