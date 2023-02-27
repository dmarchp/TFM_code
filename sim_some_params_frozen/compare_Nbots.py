import matplotlib.pyplot as plt
import pandas as pd

model = 'Galla'

#pis = [0.3, 0.3]
pis = [0.4, 0.2]
qs = [7, 10]
Ns = [35, 50]

arena_r = 20
interac_r = 7

fig, ax = plt.subplots(1,2)
for N in Ns:
    df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results.csv')
    df = df.loc[(df['arena_r'] == arena_r) & (df['interac_r'] == interac_r) & (df['pi1'] == pis[0]) & (df['pi2'] == pis[1]) & (df['q1'] == qs[0]) & (df['q2'] == qs[1])]
    ax[0].plot(df['lambda'], df['f2'], label=f"{N}")
    ax[1].plot(df['lambda'], df['Q'])
ax[0].set_xlabel(r'$\lambda$')
ax[1].set_xlabel(r'$\lambda$')
ax[0].set_ylabel(r'$f_2$')
ax[1].set_ylabel(r'$Q$')
ax[0].legend(title='N')
fig.text(0.05, 0.97, rf'$(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}, \; r_i = {interac_r}$', fontsize=9, color='xkcd:dark grey blue')
fig.tight_layout()
fig.savefig(f'compare_Nbots_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_ir_{interac_r}.png')
