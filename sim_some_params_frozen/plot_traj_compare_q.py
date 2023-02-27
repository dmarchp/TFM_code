import subprocess
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

q1s = [2, 7]
#q1s_colors_Q = ['xkcd:gray', 'xkcd:blue']
q1s_colors_Q = ['xkcd:bright red', 'xkcd:dark sky blue']
q1s_colors_f2 = ['xkcd:purple', 'xkcd:forest green']
q2_incrs = [1, 2, 3]
#q2_incrs = [4, 5, 6]
lambs = [0.0, 0.2, 0.4, 0.6, 0.8]
pi1s = [0.5, ]
pi2s = [0.5, ]
model = 'Galla'

Navg = 10

fig, ax = plt.subplots(3,5, figsize=(14,10), dpi=200)
figF, axF = plt.subplots(3,5, figsize=(14,10), dpi=200)
for pi1 in pi1s:
    for pi2 in pi2s:
        for q1 in q1s:
            for i,q2_inc in enumerate(q2_incrs):
                for j,l in enumerate(lambs):
                    subprocess.call(f'tar -xzf {model}/time_evos/time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q1+q2_inc}_l_{l}.tar.gz',shell=True)
                    for k in range(Navg):
                        df = pd.read_csv(f'time_evo_csv/time_evo_rea_'+str(k+1).zfill(3)+'.csv')
                        #df.drop(df[df.iter > 5000].index, inplace=True)
                        if(k==0):
                            Q = np.array(df['f2']-2*df['f1'])
                            f2 = np.array(df['f2'])
                        else:
                            Q += np.array(df['f2']-2*df['f1'])
                            f2 += np.array(df['f2'])
                    Q /= Navg
                    f2 /= Navg
                    ax[i,j].plot(df['iter'], Q, color=q1s_colors_Q[q1s.index(q1)], label=rf'$q_1 = {q1}$')
                    axF[i,j].plot(df['iter'], f2, color=q1s_colors_f2[q1s.index(q1)], label=rf'$q_1 = {q1}$')
                    if(i==2 and j==4):
                        handles, labels = ax[i,j].get_legend_handles_labels()
                        handlesF, labelsF = axF[i,j].get_legend_handles_labels()
                    if(i==0):
                        ax[i,j].set_title(rf'$\lambda$ = {l}')
                        axF[i,j].set_title(rf'$\lambda$ = {l}')
                    #else:
                    #    ax[i,j].set_title(rf'$\Delta q = {q2_inc}$')
                    if(j==0):
                        ax[i,j].set_ylabel(rf'Q, $\Delta q = {q2_inc}$')
                        axF[i,j].set_ylabel(rf'$f_2$, $\Delta q = {q2_inc}$')
                    ax[i,j].set_xscale('log')
                    #ax[i,j].tick_params(axis='both', labelsize=8)
                    ax[i,j].grid(axis='y', which='major', color='xkcd:gray', linestyle='-', alpha=0.6)
                    ax[i,j].grid(axis='x', which='major', color='xkcd:gray', linestyle='-', alpha=0.6)
                    #ax[i,j].grid(axis='x', which='minor', color='xkcd:gray', linestyle='-', alpha=0.6)
                    ax[i,j].minorticks_on()
                    axF[i,j].set_xscale('log')
                    axF[i,j].set_yscale('log')
                    axF[i,j].set_ylim(0.05, 1)
                    axF[i,j].set_xlim(0.7,5000)
                    axF[i,j].grid(axis='y', which='minor', color='xkcd:gray', linestyle='-', alpha=0.6)
                    axF[i,j].grid(axis='y', which='major', color='xkcd:gray', linestyle='-', alpha=0.6)
                    axF[i,j].grid(axis='x', which='major', color='xkcd:gray', linestyle='-', alpha=0.6)
                    axF[i,j].minorticks_on()
                    subprocess.call('rm -r time_evo_csv', shell=True)


fig.legend(handles, labels, loc='lower right', fontsize='x-large')
fig.tight_layout()
fig.savefig(f'time_evos_fp_Qavg_q1s_{q1s[0]}_{q1s[1]}_q2_plus_{q2_incrs[0]}{q2_incrs[1]}{q2_incrs[2]}_pi1_{pi1}_pi2_{pi2}.png')
 # , bbox_inches='tight', pad_inches=0.005

figF.legend(handlesF, labelsF, loc='lower right', fontsize='x-large')
figF.tight_layout()
figF.savefig(f'time_evos_fp_f2avg_q1s_{q1s[0]}_{q1s[1]}_q2_plus_{q2_incrs[0]}{q2_incrs[1]}{q2_incrs[2]}_pi1_{pi1}_pi2_{pi2}.png')
