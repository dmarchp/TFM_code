import pandas as pd
import matplotlib.pyplot as plt
from numpy import linspace

model = 'Galla'

pis = [0.3, 0.3]
pis = [0.4, 0.2]
qs = [7, 10]
arena_r = 20
exclusion_r = [0.0, 1.5]
interac_r = [20,13,12,11,10,9,8,7,6,5,4,3,2,1] # er 0, pi 30 30
#interac_r = [20,12,10,7,4,3,2]
# interac_r = [2, 3]
N = 35

dfer0 = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r[0]}.csv')
dfer0 = dfer0.loc[(dfer0['arena_r'] == arena_r) & (dfer0['pi1'] == pis[0]) & (dfer0['pi2'] == pis[1]) & (dfer0['q1'] == qs[0]) & (dfer0['q2'] == qs[1])]
dfer1 = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r[1]}.csv')
dfer1 = dfer1.loc[(dfer1['arena_r'] == arena_r) & (dfer1['pi1'] == pis[0]) & (dfer1['pi2'] == pis[1]) & (dfer1['q1'] == qs[0]) & (dfer1['q2'] == qs[1])]

dfmf = pd.read_csv(f'../sim_some_params/{model}/{N}_bots/sim_results.csv')
dfmf = dfmf.loc[(dfmf['pi1'] == pis[0]) & (dfmf['pi2'] == pis[1]) & (dfmf['q1'] == qs[0]) & (dfmf['q2'] == qs[1])]

def zero_interaction_f(lamb):
    f0 = 1/(1+(1-lamb)*(pis[0]*qs[0]+pis[1]*qs[1]))
    f1 = pis[0]*qs[0]*(1-lamb)*f0
    f2 = pis[1]*qs[1]*(1-lamb)*f0
    return [f0,f1,f2]
    
zeroi_fs = {'f0':[], 'f1':[], 'f2':[]}
for l in dfmf['lambda']:
    res = zero_interaction_f(l)
    zeroi_fs['f0'].append(res[0])
    zeroi_fs['f1'].append(res[1])
    zeroi_fs['f2'].append(res[2])
zeroi_fs = pd.DataFrame(zeroi_fs)

# Figure: (x-lambda, y-fs) for each ir
n = len(interac_r)
# colors = plt.cm.jet(linspace(0,1,n))
colors = plt.cm.gist_rainbow(linspace(0,1,n))
fig,ax = plt.subplots(1,3,figsize=(9,5))
for i,ir in enumerate(interac_r):
    dfir = dfer0.loc[(dfer0['interac_r'] == ir)]
    ax[0].plot(dfir['lambda'], dfir['f0'], label=f'{ir}', color=colors[i], alpha=0.6)
    ax[1].plot(dfir['lambda'], dfir['f1'], color=colors[i], alpha=0.6)
    ax[2].plot(dfir['lambda'], dfir['f2'], color=colors[i], alpha=0.6)
    dfir = dfer1.loc[(dfer1['interac_r'] == ir)]
    ax[0].plot(dfir['lambda'], dfir['f0'], color=colors[i], ls='--', alpha=0.6)
    ax[1].plot(dfir['lambda'], dfir['f1'], color=colors[i], ls='--', alpha=0.6)
    ax[2].plot(dfir['lambda'], dfir['f2'], color=colors[i], ls='--', alpha=0.6)
ax[1].set_xlabel(r'$\lambda$')
ax[0].set_ylabel(r'$f_0$')
ax[1].set_ylabel(r'$f_1$')
ax[2].set_ylabel(r'$f_2$')
ax[0].legend(title=r'$r_i$')
fig.text(0.05, 0.98, rf'$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}$, Solid: $r_e = {exclusion_r[0]}$, Dashed: $r_e = {exclusion_r[1]}$', fontsize=9, color='xkcd:dark grey blue')
fig.tight_layout()
fig.savefig(f'compare_er_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_many_ir.png')
plt.close(fig)

# Figure: (x-ir, y-f2) for some lambdas
lambdas = [0.3, 0.6, 0.9] #, 0.6, 0.9
n = len(lambdas)
colors = plt.cm.gist_rainbow(linspace(0,1,n))
fig,ax = plt.subplots()
for i,l in enumerate(lambdas):
    dfl = dfer0.loc[(dfer0['lambda'] == l)]
    ax.plot(dfl['interac_r'], dfl['f2'], label=f'{l}', color=colors[i])
    dfl = dfer1.loc[(dfer1['lambda'] == l)]
    ax.plot(dfl['interac_r'], dfl['f2'], label=f'{l}', color=colors[i], ls='--')
    ax.axhline(float(dfmf.loc[(dfmf['lambda']==l)]['f2']), xmin=0.05, xmax=1.0, color='xkcd:grey', ls=':', alpha=0.6)
    ax.axhline(y=zero_interaction_f(l)[2], xmin=0.05, xmax=0.25, color='xkcd:grey', ls='-.', alpha=0.6)
ax.set_xlabel(r'$r_i$')
ax.set_ylabel(r'$f_2$')
ax.legend(title=r'$\lambda$')
fig.text(0.05, 0.98, rf'$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}$, Solid: $r_e = {exclusion_r[0]}$, Dashed: $r_e = {exclusion_r[1]}$', fontsize=9, color='xkcd:dark grey blue')
fig.tight_layout()
fig.savefig(f'compare_er_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_many_lambda_er_{exclusion_r}.png')
plt.close(fig)

# Figure: (x-ir, y-Q) for some lambdas
lambdas = [0.3, 0.6, 0.9] #, 0.6, 0.9
n = len(lambdas)
colors = plt.cm.gist_rainbow(linspace(0,1,n))
fig,ax = plt.subplots()
for i,l in enumerate(lambdas):
    dfl = dfer0.loc[(dfer0['lambda'] == l)]
    ax.plot(dfl['interac_r'], dfl['Q'], label=f'{l}', color=colors[i])
    dfl = dfer1.loc[(dfer1['lambda'] == l)]
    ax.plot(dfl['interac_r'], dfl['Q'], label=f'{l}', color=colors[i], ls='--')
    ax.axhline(float(dfmf.loc[(dfmf['lambda']==l)]['Q']), xmin=0.05, xmax=1.0, color='xkcd:grey', ls=':', alpha=0.6)
    ax.axhline(y=zero_interaction_f(l)[2]-2*zero_interaction_f(l)[1], xmin=0.05, xmax=0.25, color='xkcd:grey', ls='-.', alpha=0.6)
ax.set_xlabel(r'$r_i$')
ax.set_ylabel(r'$Q$')
ax.legend(title=r'$\lambda$')
fig.text(0.05, 0.98, rf'$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}$, Solid: $r_e = {exclusion_r[0]}$, Dashed: $r_e = {exclusion_r[1]}$', fontsize=9, color='xkcd:dark grey blue')
fig.tight_layout()
fig.savefig(f'compare_er_Q_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_many_lambda_er_{exclusion_r}.png')
plt.close(fig)
