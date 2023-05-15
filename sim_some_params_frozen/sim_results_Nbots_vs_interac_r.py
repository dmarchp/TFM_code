import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

model = 'Galla'
pis = [0.3, 0.3]
qs = [7, 10]
#lamb = 0.6
lambs = [0.3, 0.6, 0.9]
#lambs_colors_r = plt.cm.YlOrBr(np.linspace(0.1,0.9,len(lambs)))
#lambs_colors_N = plt.cm.BuGn(np.linspace(0.1,0.9,len(lambs)))
lambs_colors_r = plt.cm.spring(np.linspace(0.1,0.9,len(lambs)))
lambs_colors_N = plt.cm.winter(np.linspace(0.1,0.9,len(lambs)))
#alpha_l = [0.4, 0.7, 1]
arena_r = 20
exclusion_r = 1.5
perc_r = 6.5
perc_r = 103.67*35**(-0.76)

fig, ax = plt.subplots(1,3, figsize=(9,5))
# figAlt, axAlt = plt.subplots()


# fix N, move interaction radius:
N = 35
df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}_NOPUSH.csv')
df = df.loc[(df['arena_r']==arena_r) & (df['pi1']==pis[0]) & (df['pi2']==pis[1]) & (df['q1']==qs[0]) & (df['q2']==qs[1])]
df = df[df.interac_r != 20.0]
df = df.rename(columns={"lambda":"lamb"})
for l,lcolor in zip(lambs,lambs_colors_r):
    #dfl = df.loc[(df['lambda']==l)]
    dfl = df.query('lamb == @l')
    ax[0].plot(dfl['interac_r'], dfl['f2'], color=lcolor, marker='2', markersize=3, label=f'{l}', lw=0.8)
    # ax[2].plot(N*dfl['interac_r']**2/arena_r**2, dfl['f2'], color=lcolor, marker='2', markersize=3, lw=0.8)
    # ax[2].plot(N*dfl['interac_r']**2/(arena_r*perc_r)**2, dfl['f2'], color=lcolor, marker='2', markersize=3, lw=0.8)
    ax[2].plot((dfl['interac_r']/perc_r)**2, dfl['f2'], color=lcolor, marker='2', markersize=3, lw=0.8)
    # axAlt.plot((dfl['interac_r']/perc_r)**2, (N/arena_r**2)*dfl['f2'], color=lcolor, marker='.', markersize=3, lw=0.8)
    
# data to file:
dfls = df.query('lamb in @lambs').copy()
dfls['Dc'] = N*dfls['interac_r']**2/(arena_r*perc_r)**2
dfls = dfls.drop(columns=['m', 'sdm', 'k0', 'k1', 'k2', 'sdk0', 'sdk1', 'sdk2'])
dfls.to_csv(f'results_dif_ir_N_{N}.csv', index=False)
    
ax[0].legend(title='$\lambda$', fontsize=8)

# fix interaction radius, move N:
lambsdf, Nsdf, f1df, f2df, dcdf = [], [], [], [], []
interac_r = 6.5
Ns = [10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80]
perc_rs = [13.0, 11.0, 9.2, 7.8, 7.5, 6.4, 5.8, 5.0, 4.6, 4.2, 4.0]
for l,lcolor in zip(lambs,lambs_colors_N):
    f1_dif_N, f2_dif_N = [], []
    for N in Ns:
        df = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}_NOPUSH.csv')
        df = df.rename(columns={"lambda":"lamb"})
        #df = df.loc[(df['arena_r']==arena_r) & (df['pi1']==pis[0]) & (df['pi2']==pis[1]) & (df['q1']==qs[0]) & (df['q2']==qs[1]) & (df['lambda']==l) & (df['interac_r']==interac_r)]
        df = df.query('arena_r == @arena_r & pi1 == @pis[0] & pi2 == @pis[1] & q1 == @qs[0] & q2 == @qs[1] & lamb == @l & interac_r == @interac_r')
        # print(df['f1'])
        f1_dif_N.append(float(df['f1'].iloc[0])), f2_dif_N.append(float(df['f2'].iloc[0]))
    ax[1].plot(Ns, f2_dif_N, color=lcolor, marker='2', markersize=3, label=f'{l}', lw=0.8)
    # ax[2].plot(np.array(Ns)*(interac_r/arena_r)**2, f2_dif_N, color=lcolor, marker='2', markersize=3, lw=0.8)
    # ax[2].plot(np.array(Ns)*(interac_r/(arena_r*perc_r))**2, f2_dif_N, color=lcolor, marker='2', markersize=3, lw=0.8)
    # ax[2].plot((interac_r/np.array(perc_rs))**2, f2_dif_N, color=lcolor, marker='2', markersize=3, lw=0.8)
    # ax[2].plot((interac_r/(62.067*np.array(Ns)**(-0.633)))**2, f2_dif_N, color=lcolor, marker='2', markersize=3, lw=0.8)
    # ax[2].plot((interac_r/(42*np.array(Ns)**(-0.5)))**2, f2_dif_N, color=lcolor, marker='2', markersize=3, lw=0.8)
    ax[2].plot((interac_r/(58.11*np.array(Ns)**(-0.615)))**2, f2_dif_N, color=lcolor, marker='2', markersize=3, lw=0.8)
    dc = list(np.array(Ns)*(interac_r/(arena_r*perc_r))**2)
    lambsdf.extend([l]*len(Ns)), Nsdf.extend(Ns), f1df.extend(f1_dif_N), f2df.extend(f2_dif_N), dcdf.extend(dc)

# data to file:
dfNs = pd.DataFrame({'lambs':lambsdf, 'N':Nsdf, 'f1':f1df, 'f2':f2df, 'Dc':dcdf})
dfNs['Q'] = dfNs['f2'] - 2*dfNs['f1']
dfNs['Dc'] = dfNs['N']*interac_r**2/(arena_r*perc_r)**2
dfNs.to_csv(f'results_dif_N_ir_{interac_r}.csv', index=False)
    
    
ax[1].legend(title='$\lambda$', fontsize=8)


ax[0].set_xlabel('$r_i$')
ax[1].set_xlabel('$N$')
#ax[2].set_xlabel('$N \cdot (r_i / r_a)^{2}$')
# ax[2].set_xlabel(r'$N \cdot (\frac{r_i}{r_i^{*} r_a})^{2}$')
ax[2].set_xlabel(r'$(r_{{int}}/r_{{int}}^*)^2$')
# ax[2].set_xlim(0.02, 0.14) # when plotting as a function of N*(ri/rperc)**2 / R**2
# ax[2].set_xlim(None, 5) # when plotting as a function of N*(ri/R)**2
ax[2].set_xlim(None, 1.2) # when plotting as a function of (ri/ri*)**2
ax[0].set_ylabel('$f_2$')
#fig.legend(title='$\lambda$', bbox_to_anchor=(0.09, 0.87, 0.08, 0.08))

fig.tight_layout()
fig.savefig(f'f2_vs_ri_or_Nbots_ar_{arena_r}_er_{exclusion_r}.png')


# axAlt.set(xlabel=r'$(\frac{r_i}{r_i^{*}})^{2}$', ylabel='f2*dens')
# figAlt.tight_layout()
# figAlt.savefig('crowding_proves.png')
