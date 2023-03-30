import pandas as pd
import matplotlib.pyplot as plt
from numpy import linspace
from subprocess import call

# idea for creating sequential colors
# https://stackoverflow.com/questions/38208700/matplotlib-plot-lines-with-colors-through-colormap

model = 'Galla'

pis = [0.3, 0.3]
#pis = [0.4, 0.2]
qs = [7, 10]
arena_r = 20
exclusion_r = 1.5
# puc fer servir tots els ir, quan no estigui simulat el df quedarà buit pero el programa no peta
# interac_r = [20,13,12,11,10,9,8,7,6,5,4,3,2] # er 0, pi 30 30
#interac_r = [20,13,12,11,10,9,8,7,6,5,4,3.9,3.8,3.7,3.6,3.5,3.4,3.3,3.2,3.1,3,2]
# interac_r = [12,10,8,7,6,5,4.8,4.5,4.2,4,3.9,3.8,3.7,3.6,3.5,3.4,3.3,3.2,3.1,3]
#interac_r = [20,12,10,7,4,3,2]
interac_r = linspace(3,12,19)
N = 35

df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}_NOPUSH.csv') # _NOPUSH
df = df.loc[(df['arena_r'] == arena_r) & (df['pi1'] == pis[0]) & (df['pi2'] == pis[1]) & (df['q1'] == qs[0]) & (df['q2'] == qs[1])]

# mean field values:
# from the simulations...
# dfmf = pd.read_csv(f'../sim_some_params/{model}/{N}_bots/sim_results.csv')
# dfmf = dfmf.loc[(dfmf['pi1'] == pis[0]) & (dfmf['pi2'] == pis[1]) & (dfmf['q1'] == qs[0]) & (dfmf['q2'] == qs[1])]
# dfmf.reset_index(inplace=True)
# or from the equation...
fs = [[],[],[]]
lambs = list(pd.unique(df['lambda']))
for l in lambs:
    call(f'python ../det_sols_from_polynomial/f0poly_sols_clean.py {pis[0]} {pis[1]} {qs[0]} {qs[1]} {l} > sols.dat', shell=True)
    with open('sols.dat', 'r') as file:
        sols = [float(f) for f in file.readline().split()]
        fs[0].append(sols[0]), fs[1].append(sols[1]), fs[2].append(sols[2])
dfmf = pd.DataFrame({'lambda':lambs, 'f0':fs[0], 'f1':fs[1], 'f2':fs[2]})

# zero interaction values:
def zero_interaction_f(lamb):
    f0 = 1/(1+(1-lamb)*(pis[0]*qs[0]+pis[1]*qs[1]))
    f1 = pis[0]*qs[0]*(1-lamb)*f0
    f2 = pis[1]*qs[1]*(1-lamb)*f0
    return [f0,f1,f2]

zeroi_fs = {'lambda':[], 'f0':[], 'f1':[], 'f2':[]}
for l in dfmf['lambda']:
    zeroi_fs['lambda'].append(l)
    res = zero_interaction_f(l)
    zeroi_fs['f0'].append(res[0])
    zeroi_fs['f1'].append(res[1])
    zeroi_fs['f2'].append(res[2])
zeroi_fs = pd.DataFrame(zeroi_fs)

# Figure: (x-lambda, y-fs) for each ir
n = len(interac_r)
colors = plt.cm.gist_rainbow(linspace(0,1,n))
fig,ax = plt.subplots(1,3,figsize=(9,5))
for i,ir in enumerate(interac_r):
    dfir = df.loc[(df['interac_r'] == ir)]
    ax[0].plot(dfir['lambda'], dfir['f0'], label=f'{ir}', color=colors[i], lw=0.8)
    ax[1].plot(dfir['lambda'], dfir['f1'], color=colors[i], lw=0.8)
    ax[2].plot(dfir['lambda'], dfir['f2'], color=colors[i], lw=0.8)
ax[0].plot(dfmf['lambda'], dfmf['f0'], label=f'MF', color='k', ls='-.', alpha=0.6, lw=0.8)
ax[1].plot(dfmf['lambda'], dfmf['f1'], color='k', ls='-.', alpha=0.6, lw=0.8)
ax[2].plot(dfmf['lambda'], dfmf['f2'], color='k', ls='-.', alpha=0.6, lw=0.8)
ax[0].plot(dfmf['lambda'], zeroi_fs['f0'], label='0', color='k', ls='--', alpha=0.6, lw=0.8)
ax[1].plot(dfmf['lambda'], zeroi_fs['f1'], color='k', ls='--', alpha=0.6, lw=0.8)
ax[2].plot(dfmf['lambda'], zeroi_fs['f2'], color='k', ls='--', alpha=0.6, lw=0.8)
ax[1].set_xlabel(r'$\lambda$')
ax[0].set_ylabel(r'$f_0$')
ax[1].set_ylabel(r'$f_1$')
ax[2].set_ylabel(r'$f_2$')
ax[0].legend(title=r'$r_i$', fontsize=8)
fig.text(0.05, 0.98, rf'$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; N = {N},\; r_a = {arena_r}, \; r_e = {exclusion_r}$', fontsize=9, color='xkcd:dark grey blue')
fig.tight_layout()
fig.savefig(f'compare_ir_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_N_{N}_ar_{arena_r}_many_ir_er_{exclusion_r}_NOPUSH.png')
plt.close(fig)

# Figure: (x-ir, y-f2) for some lambdas
# lambdas = [0.0, 0.3, 0.6, 0.9]
# n = len(lambdas)
# colors = plt.cm.gist_rainbow(linspace(0,1,n))
# fig,ax = plt.subplots()
# for i,l in enumerate(lambdas):
#     dfl = df.loc[(df['lambda'] == l)]
#     ax.plot(dfl['interac_r'], dfl['f2'], label=f'{l}', color=colors[i]) # ara no recordo peruqe feia dfl['interac_r']**2
#     ax.axhline(float(dfmf.loc[(dfmf['lambda']==l)]['f2']), color=colors[i], ls='--', alpha=0.6)
#     ax.axhline(y=zero_interaction_f(l)[2], xmin=0, xmax=0.125, color=colors[i], ls='-.', alpha=0.6)
# ax.set_xlabel(r'$i_r$')
# ax.set_ylabel(r'$f_2$')
# ax.legend(title=r'$\lambda$')
# fig.text(0.05, 0.98, rf'$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}, \; r_e = {exclusion_r}$', fontsize=9, color='xkcd:dark grey blue')
# fig.tight_layout()
# fig.savefig(f'compare_ir_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_many_lambda_er_{exclusion_r}.png')
# plt.close(fig)

################################################################################################################################
# Figure: (x-lambda, y-newk2) for each ir
# interac_r = [20,12,11,10,9,8,7,6,5,4,3,2]
# n = len(interac_r)
# colors = plt.cm.gist_rainbow(linspace(0,1,n))
# fig,ax = plt.subplots()
# fig2, ax2 = plt.subplots(1,3,figsize=(9,5))
# for i,ir in enumerate(interac_r):
#     dfir = df.loc[(df['interac_r'] == ir)].copy()
#     dfir.reset_index(inplace=True)
#     # Alternativa 1, fent servir els resultats del limit lambda 1
#     dfir['newk0'] = (dfir['f0'] - zeroi_fs['f0'])/(pd.Series([1/qs[1]]*len(dfir['lambda']), dtype='float64') - zeroi_fs['f0'])
#     dfir['newk1'] = (dfir['f1'] - zeroi_fs['f1'])/(pd.Series([0]*len(dfir['lambda']), dtype='float64') - zeroi_fs['f1'])
#     dfir['newk2'] = (dfir['f2'] - zeroi_fs['f2'])/(pd.Series([1-1/qs[1]]*len(dfir['lambda']), dtype='float64') - zeroi_fs['f2'])
#     # Alternativa 2, fent servir els resultats de mean field, depenents de lambda
#     # dfir['newk0'] = (dfir['f0'] - zeroi_fs['f0'])/(dfmf['f0'] - zeroi_fs['f0'])
#     # dfir['newk1'] = (dfir['f1'] - zeroi_fs['f1'])/(dfmf['f1'] - zeroi_fs['f1'])
#     # dfir['newk2'] = (dfir['f2'] - zeroi_fs['f2'])/(dfmf['f2'] - zeroi_fs['f2'])
#     ax.plot(dfir['lambda'], dfir['newk2'], label=f'{ir}', color=colors[i])
#     ax2[0].plot(dfir['lambda'], dfir['newk0'], label=f'{ir}', color=colors[i])
#     ax2[1].plot(dfir['lambda'], dfir['newk1'], color=colors[i])
#     ax2[2].plot(dfir['lambda'], dfir['newk2'], color=colors[i])
# # ax[0].plot(dfmf['lambda'], dfmf['f0'], label=f'MF', color='k', ls='--', alpha=0.6)
# # ax[1].plot(dfmf['lambda'], dfmf['f1'], color='k', ls='--', alpha=0.6)
# # ax[2].plot(dfmf['lambda'], dfmf['f2'], color='k', ls='--', alpha=0.6)
# # ax[0].plot(dfmf['lambda'], zeroi_fs['f0'], label='0', color='k', ls='-.', alpha=0.6)
# # ax[1].plot(dfmf['lambda'], zeroi_fs['f1'], color='k', ls='-.', alpha=0.6)
# # ax[2].plot(dfmf['lambda'], zeroi_fs['f2'], color='k', ls='-.', alpha=0.6)
# ax.set_xlabel(r'$\lambda$')
# ax.set_ylabel(r'$k_2$')
# ax.legend(title=r'$r_i$')
# fig.text(0.05, 0.98, rf'$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}, \; r_e = {exclusion_r}$', fontsize=9, color='xkcd:dark grey blue')
# fig.tight_layout()
# fig.savefig(f'newk2_compare_ir_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_many_ir_er_{exclusion_r}.png')
# plt.close(fig)
# ax2[0].legend(title=r'$r_i$')
# for a in ax2:
#     a.set_xlabel(f'$\lambda$')
# ax2[0].set_ylabel('$k_0$')
# ax2[1].set_ylabel('$k_1$')
# ax2[2].set_ylabel('$k_2$')
# fig2.text(0.05, 0.98, rf'$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}, \; r_e = {exclusion_r}$', fontsize=9, color='xkcd:dark grey blue')
# fig2.tight_layout()
# fig2.savefig(f'newks_compare_ir_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_many_ir_er_{exclusion_r}.png')
# plt.close(fig2)


# Figure: (x-ir, y-newk2) for some lambdas
# lambdas = [0.0, 0.3, 0.6, 0.9]
# n = len(lambdas)
# colors = plt.cm.gist_rainbow(linspace(0,1,n))
# fig,ax = plt.subplots()
# for i,l in enumerate(lambdas):
#     dfl = df.loc[(df['lambda'] == l)].copy()
#     dfl.reset_index(inplace=True)
#     # Alternativa 1, fent servir els resultats del limit lambda 1
#     aux = pd.Series([1-1/qs[1]]*len(dfl['interac_r']), dtype='float64')
#     # Alternativa 2, fent servir els resultats de mean field, depenents de lambda
#     # aux = dfmf['f2']
#     aux2 = pd.Series([zeroi_fs['f2'].loc[(zeroi_fs['lambda']==l)]]*len(dfl['interac_r']))
#     dfl['newk2'] = (dfl['f2'] - aux2)/(aux - aux2)
#     ax.plot(dfl['interac_r'], dfl['newk2'], label=f'{l}', color=colors[i])
#     #ax.axhline(float(dfmf.loc[(dfmf['lambda']==l)]['f2']), color=colors[i], ls='--', alpha=0.6)
#     #ax.axhline(y=zero_interaction_f(l)[2], xmin=0, xmax=0.125, color=colors[i], ls='-.', alpha=0.6)
# ax.set_xlabel(r'$i_r$')
# ax.set_ylabel(r'$k_2$')
# ax.legend(title=r'$\lambda$')
# fig.text(0.05, 0.98, rf'$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}, \; r_e = {exclusion_r}$', fontsize=9, color='xkcd:dark grey blue')
# fig.tight_layout()
# fig.savefig(f'compare_ir_newk2_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_er_{exclusion_r}_many_lambda.png')
# plt.close(fig)
