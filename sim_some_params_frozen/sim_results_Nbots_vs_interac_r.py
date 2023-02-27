import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

model = 'Galla'
pis = [0.3, 0.3]
qs = [7, 10]
#lamb = 0.6
lambs = [0.3, 0.6, 0.9]
alpha_l = [0.4, 0.7, 1]
arena_r = 20
exclusion_r = 1.5

fig, ax = plt.subplots(1,3, figsize=(9,5))

# fix N, move interaction radius:
N = 35
df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}.csv')
df = df.loc[(df['arena_r']==arena_r) & (df['pi1']==pis[0]) & (df['pi2']==pis[1]) & (df['q1']==qs[0]) & (df['q2']==qs[1])]
df = df[df.interac_r != 20.0]
for l,al in zip(lambs,alpha_l):
    dfl = df.loc[(df['lambda']==l)]
    ax[0].plot(dfl['interac_r'], dfl['f2'], color='xkcd:red', alpha = al, label=f'{l}')
    ax[2].plot(N*dfl['interac_r']**2/arena_r**2, dfl['f2'], color='xkcd:red', alpha=al)

# fix interaction radius, move N:
interac_r = 7.0
Ns = [5, 10, 20, 30, 35, 40, 50, 60, 70, 80, 90]
for l,al in zip(lambs,alpha_l):
    f2_dif_N = []
    for N in Ns:
        df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}.csv')
        df = df.loc[(df['arena_r']==arena_r) & (df['pi1']==pis[0]) & (df['pi2']==pis[1]) & (df['q1']==qs[0]) & (df['q2']==qs[1]) & (df['lambda']==l) & (df['interac_r']==interac_r)]
        f2_dif_N.append(float(df['f2']))
    ax[1].plot(Ns, f2_dif_N, color='xkcd:blue', alpha = al)
    ax[2].plot(np.array(Ns)*(interac_r/arena_r)**2, f2_dif_N, color='xkcd:blue', alpha = al)

ax[0].set_xlabel('$r_i$')
ax[1].set_xlabel('$N$')
ax[2].set_xlabel('$N \cdot (r_i / r_a)^{2}$')
ax[0].set_ylabel('$f_2$')
fig.legend(title='$\lambda$', bbox_to_anchor=(0.09, 0.87, 0.08, 0.08))

fig.tight_layout()
fig.savefig(f'f2_vs_ri_or_Nbots_ar_{arena_r}_er_{exclusion_r}.png')