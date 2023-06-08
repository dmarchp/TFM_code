import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

model = 'Galla'
pis = [0.3, 0.3]
qs = [7, 10]
lambs = [0.3, 0.6, 0.9]
lambs_colors_r = plt.cm.spring(np.linspace(0.1,0.9,len(lambs)))
lambs_colors_N = plt.cm.winter(np.linspace(0.1,0.9,len(lambs)))
lambs_colors = plt.cm.gnuplot(np.linspace(0.05, 0.9,len(lambs)))
arena_r = 20
exclusion_r = 1.5
perc_r = 6.5

exponent_rint_frac = 2

def perc_r(N):
    return 58.11*N**(-0.615)

fig, ax = plt.subplots()

# QUENCHED
# fix N, move interaction radius:
N = 35
perc_r_fixN = perc_r(N)
df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}_NOPUSH.csv')
df = df.loc[(df['arena_r']==arena_r) & (df['pi1']==pis[0]) & (df['pi2']==pis[1]) & (df['q1']==qs[0]) & (df['q2']==qs[1])]
df = df[df.interac_r != 20.0]
df = df.rename(columns={"lambda":"lamb"})
for l,lcolor in zip(lambs,lambs_colors):
    dfl = df.query('lamb == @l')
    if l==0.3:
        ax.plot((dfl['interac_r']/perc_r_fixN)**exponent_rint_frac, dfl['f2'], color=lcolor, marker='1', markersize=5, lw=0.8, label=r'Quenched, var $r_i$')
    else:
        ax.plot((dfl['interac_r']/perc_r_fixN)**exponent_rint_frac, dfl['f2'], color=lcolor, marker='1', markersize=5, lw=0.8)



# QUENCHED
# fix r_i, move N:
interac_r = 6.5
Ns = [10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80]
for l,lcolor in zip(lambs,lambs_colors):
    f1_dif_N, f2_dif_N = [], []
    for N in Ns:
        df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}_NOPUSH.csv')
        df = df.rename(columns={"lambda":"lamb"})
        df = df.query('arena_r == @arena_r & pi1 == @pis[0] & pi2 == @pis[1] & q1 == @qs[0] & q2 == @qs[1] & lamb == @l & interac_r == @interac_r')
        f1_dif_N.append(float(df['f1'].iloc[0])), f2_dif_N.append(float(df['f2'].iloc[0]))
    interac_r_perc = perc_r(np.array(Ns))
    if l==0.3:
        ax.plot((interac_r/interac_r_perc)**exponent_rint_frac, f2_dif_N, color=lcolor, marker='.', markersize=5, lw=0.8, ls='-.', label=r'Quenched, var $N$')
    else:
        ax.plot((interac_r/interac_r_perc)**exponent_rint_frac, f2_dif_N, color=lcolor, marker='.', markersize=5, lw=0.8, ls='-.')


factor = 4.0/6.5
# KILOMBO
# fix r_i, move N:
interac_r = 5.0
df = pd.read_csv('other_res_files/kilomboStatValues_variableN.csv')
df = df.rename(columns={"lambda":"lamb"})
df = df.query("parameter == 'f2'")
for l,lcolor in zip(lambs,lambs_colors):
    dfl = df.query('lamb == @l').copy()
    dfl['frac_ir'] = interac_r/(factor*perc_r(dfl['N']))
    if l==0.3:
        ax.plot(dfl['frac_ir']**exponent_rint_frac, dfl['stat.value'], color=lcolor, marker='x', markersize=4, lw=0.0, label='Kilombo')
    else:
        ax.plot(dfl['frac_ir']**exponent_rint_frac, dfl['stat.value'], color=lcolor, marker='x', markersize=4, lw=0.0)


# KILOBOTS
# fix r_i, move N:
interac_r = 7.0
df = pd.read_csv('other_res_files/KilobotsStatValues_VaryingN.csv')
df = df.rename(columns={"lambda":"lamb"})
df = df.query("parameter == 'f2' & pi1 == @pis[0] & pi2 == @pis[1]")
for l,lcolor in zip(lambs,lambs_colors):
    dfl = df.query('lamb == @l').copy()
    dfl['frac_ir'] = interac_r/(factor*perc_r(dfl['N']))
    if l==0.3:
        ax.plot(dfl['frac_ir']**exponent_rint_frac, dfl['stat.value'], color=lcolor, marker='s', markersize=4, lw=0.0, label='Kilobots')
    else:
        ax.plot(dfl['frac_ir']**exponent_rint_frac, dfl['stat.value'], color=lcolor, marker='s', markersize=4, lw=0.0)

ax.set(xlabel=r'$(r_i / r_i^{*})^{2}$', ylabel=r'$f_2$')
fig.text(0.1,0.97, rf"$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]})$, $\lambda = [0.3, 0.6, 0.9]$", fontsize=9)
fig.legend(loc=(0.7,0.15), fontsize=10)
fig.tight_layout()
fig.savefig('provant_scaling.png')