import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('../')
from package_global_functions import *

# aqui la idea es que representem els resultats en funció de de p/pc o p*, i.e. la densitat de percolació
# on pc = (N*ri**2/R**2)c, sent qualsevol de les variables la crítica
# per exemple a partir dels radis de percolació a diferetns N (R fixe) obtenim una relació
# pc = a + b*N^(-1/(nu*df))
# pero en lloc de treure els valors de pc d'aquesta relació, fem servir igualment la relació
# ri_c = a*N**b 

latexFont(ticklabelssize=12,labelsize=14) # ticklabelssize=10, labelsize=12, legendsize=8

model = 'Galla'
pis = [0.3, 0.3]
qs = [7, 10]
lambs = [0.3, 0.6, 0.9]
lambs_colors_r = plt.cm.spring(np.linspace(0.1,0.9,len(lambs)))
lambs_colors_N = plt.cm.winter(np.linspace(0.1,0.9,len(lambs)))
lambs_colors = plt.cm.gnuplot(np.linspace(0.05, 0.9,len(lambs)))
lambs_colors = ['xkcd:blue', 'xkcd:green', 'xkcd:orange']
arena_r = 20
exclusion_r = 1.5
# perc_r = 6.5

# percolation exponents:
nu, df_expo = 4/3, 182/96

def perc_dens(N:int):
    return 11.356*N**(-1/(nu*df_expo)) + 0.939

def perc_r(N):
    return 58.11*N**(-0.615)

fig, ax = plt.subplots()
# for the definitive ffigure:
fig, ax = plt.subplots(1,1,figsize=(3.7,3.4))
ax.set(xlim=(None,2.25))

# QUENCHED
# fix N, move interaction radius:
N = 35
perc_dens_fixN = perc_dens(N)
perc_r_fixN = perc_r(N)
df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}_NOPUSH.csv')
df = df.loc[(df['arena_r']==arena_r) & (df['pi1']==pis[0]) & (df['pi2']==pis[1]) & (df['q1']==qs[0]) & (df['q2']==qs[1])]
df = df[df.interac_r != 20.0]
df = df.rename(columns={"lambda":"lamb"})
for l,lcolor in zip(lambs,lambs_colors):
    dfl = df.query('lamb == @l')
    if l==0.3:
        # ax.plot((N*dfl['interac_r']**2/arena_r**2)/perc_dens_fixN, dfl['f2'], color=lcolor, marker='1', markersize=5, lw=0.8, label=r'Quenched, var $r_i$')
        ax.plot((dfl['interac_r']/perc_r_fixN)**2, dfl['f2'], color=lcolor, marker='1', markersize=5, lw=0.8, alpha=0.75, label=r'Quenched, var $r_i$')
    else:
        # ax.plot((N*dfl['interac_r']**2/arena_r**2)/perc_dens_fixN, dfl['f2'], color=lcolor, marker='1', markersize=5, lw=0.8)
        ax.plot((dfl['interac_r']/perc_r_fixN)**2, dfl['f2'], color=lcolor, marker='1', markersize=5, lw=0.8, alpha=0.75)

# QUENCHED
# fix r_i, move N:
interac_r = 6.5
Ns = [10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80]
# in this case we should know de Nc for this particular val of the interac_r, and p/pc = N/Nc
# as we don't know this, we do p/pc = (interac_r/interac_r_c(N))**2
for l,lcolor in zip(lambs,lambs_colors):
    f1_dif_N, f2_dif_N = [], []
    for N in Ns:
        df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}_NOPUSH.csv')
        df = df.rename(columns={"lambda":"lamb"})
        df = df.query('arena_r == @arena_r & pi1 == @pis[0] & pi2 == @pis[1] & q1 == @qs[0] & q2 == @qs[1] & lamb == @l & interac_r == @interac_r')
        f1_dif_N.append(float(df['f1'].iloc[0])), f2_dif_N.append(float(df['f2'].iloc[0]))
    perc_dens_q = perc_dens(np.array(Ns))
    perc_r_difN = perc_r(np.array(Ns))
    if l==0.3:
        # ax.plot((np.array(Ns)*interac_r**2/arena_r**2)/perc_dens_q, f2_dif_N, color=lcolor, marker='.', markersize=5, lw=0.8, ls='-.', label=r'Quenched, var $N$')
        ax.plot((interac_r/perc_r_difN)**2, f2_dif_N, color=lcolor, marker='.', markersize=5, lw=0.8, alpha=0.75, ls='-.', label=r'Quenched, var $N$')
    else:
        # ax.plot((np.array(Ns)*interac_r**2/arena_r**2)/perc_dens_q, f2_dif_N, color=lcolor, marker='.', markersize=5, lw=0.8, ls='-.')
        ax.plot((interac_r/perc_r_difN)**2, f2_dif_N, color=lcolor, marker='.', markersize=5, lw=0.8, alpha=0.75, ls='-.')


factor = 4.0/6.5
factor = 4.0/7.0
# factor = 0.5
# KILOMBO
# fix r_i, move N:
interac_r = 5.0

# Julia's Data:
df = pd.read_csv('other_res_files/kilomboStatValues_variableN.csv')
df = df.rename(columns={"lambda":"lamb"})
df = df.query("parameter == 'f2'")
for l,lcolor in zip(lambs[0:1],lambs_colors[0:1]):
    dfl = df.query('lamb == @l').copy()
    dfl['perc_dens'] = factor**2 * perc_dens(dfl['N'])
    dfl['perc_r'] = factor * perc_r(dfl['N'])
    if l==0.3:
        # ax.plot(dfl['N']*(interac_r/arena_r)**2/dfl['perc_dens'], dfl['stat.value'], color=lcolor, marker='x', markersize=4, lw=0.0, label='Kilombo')
        ax.plot((interac_r/dfl['perc_r'])**2, dfl['stat.value'], color=lcolor, marker='x', markersize=4, lw=0.0, label='Kilombo')
    else:
        # ax.plot(dfl['N']*(interac_r/arena_r)**2/dfl['perc_dens'], dfl['stat.value'], color=lcolor, marker='x', markersize=4, lw=0.0)
        ax.plot((interac_r/dfl['perc_r'])**2, dfl['stat.value'], color=lcolor, marker='x', markersize=4, lw=0.0)

# Ezequiel's data:
for l,lcolor in zip(lambs[1:],lambs_colors[1:]):
    dfl = pd.read_csv(f'other_res_files/av_freq_vs_N_lambda{l}_c100.dat', sep='\s+', names=['N', 'f0', 'f1', 'f2', 'Ndata'])
    dfl['perc_dens'] = factor**2 * perc_dens(dfl['N'])
    dfl['perc_r'] = factor * perc_r(dfl['N'])
    if l==0.3:
        # ax.plot(dfl['N']*(interac_r/arena_r)**2/dfl['perc_dens'], dfl['stat.value'], color=lcolor, marker='x', markersize=4, lw=0.0, label='Kilombo')
        ax.plot((interac_r/dfl['perc_r'])**2, dfl['f2'], color=lcolor, marker='x', markersize=4, lw=0.0, label='Kilombo')
    else:
        # ax.plot(dfl['N']*(interac_r/arena_r)**2/dfl['perc_dens'], dfl['stat.value'], color=lcolor, marker='x', markersize=4, lw=0.0)
        ax.plot((interac_r/dfl['perc_r'])**2, dfl['f2'], color=lcolor, marker='x', markersize=4, lw=0.0)


# KILOBOTS (Julia's Data)
# fix r_i, move N:
# interac_r = 7.0
# df = pd.read_csv('other_res_files/KilobotsStatValues_VaryingN.csv')
# df = df.rename(columns={"lambda":"lamb"})
# df = df.query("parameter == 'f2' & pi1 == @pis[0] & pi2 == @pis[1]")
# for l,lcolor in zip(lambs,lambs_colors):
#     dfl = df.query('lamb == @l').copy()
#     dfl['perc_dens'] = factor**2 * perc_dens(dfl['N'])
#     dfl['perc_r'] = factor * perc_r(dfl['N'])
#     if l==0.3:
#         # ax.plot(dfl['N']*(interac_r/arena_r)**2/dfl['perc_dens'], dfl['stat.value'], color=lcolor, marker='s', markersize=4, lw=0.0, label='Kilobots')
#         ax.plot((interac_r/dfl['perc_r'])**2, dfl['stat.value'], color=lcolor, marker='s', markersize=4, lw=0.0, label='Kilobots')
#     else:
#         # ax.plot(dfl['N']*(interac_r/arena_r)**2/dfl['perc_dens'], dfl['stat.value'], color=lcolor, marker='s', markersize=4, lw=0.0)
#         ax.plot((interac_r/dfl['perc_r'])**2, dfl['stat.value'], color=lcolor, marker='s', markersize=4, lw=0.0)


# KILOBOTS (David's Data)
# fix r_i, move N:
# factor = 0.5*7.0/5.0
interac_r = 5.0
jitterer_xax = [-0.04, 0.0, 0.04]
df = pd.read_csv('other_res_files/kilobot_statVals_varN_varl_useLastIters_150_pi1_0.3_pi2_0.3_q1_7_q2_10.csv')
for l,lcolor,jit in zip(lambs,lambs_colors,jitterer_xax):
    dfl = df.query('lamb == @l').copy()
    dfl['perc_r'] = factor * perc_r(dfl['N'])
    if l==0.3:
        # ax.plot((interac_r/dfl['perc_r'])**2, dfl['avg'], color=lcolor, marker='s', markersize=4, lw=0.0, label='Kilobots')
        ax.errorbar((interac_r/dfl['perc_r'])**2+jit, dfl['avg'], dfl['std_trajs'], color=lcolor, marker='s', markersize=4, lw=0.0, 
                    elinewidth=0.7, capsize=2.0, label='Kilobots')
    else:
        # ax.plot((interac_r/dfl['perc_r'])**2, dfl['avg'], color=lcolor, marker='s', markersize=4, lw=0.0)
        ax.errorbar((interac_r/dfl['perc_r'])**2+jit, dfl['avg'], dfl['std_trajs'], color=lcolor, marker='s', markersize=4, lw=0.0, 
                    elinewidth=0.7, capsize=2.0)





ax.set(xlabel=r'$(p/ p_c)$', ylabel=r'$f_2$') # , xscale='log'

# fig.text(0.1,0.97, rf"$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]})$, $\lambda = [0.3, 0.6, 0.9]$", fontsize=9)

# usual testing figure
# fig.legend(loc=(0.7,0.15), fontsize=10)
# definitive paper figure:
fig.legend(loc=(0.57,0.20), fontsize=10, frameon=False)
fig.tight_layout(pad=0.3)
fig.savefig('provant_scaling_v2.png')