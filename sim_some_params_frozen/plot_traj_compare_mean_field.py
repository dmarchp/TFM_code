import subprocess
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sys import argv

freq_colors = ['xkcd:purple', 'xkcd:light purple'] # frozen, mean field
cons_colors = ['xkcd:dark red', 'xkcd:pinkish red']

#if(len(argv)==1):
#    pi1 = float("Enter pi1
#    q1 = int(input("Enter q1: "))
#    flag_w = input


q1 = 2
q2_incrs = [1,2,3]
#q2_incrs = [4,5,6]
lambs = [0.0, 0.2, 0.4, 0.6, 0.8]
pi1s = [0.1, ]
pi2s = [0.1, ]
model = 'Galla'

Navg = 10

fig, ax = plt.subplots(3,5, figsize=(14,10), dpi=200)
figF, axF = plt.subplots(3,5, figsize=(14,10), dpi=200)
for pi1 in pi1s:
    for pi2 in pi2s:
        for i,q2_inc in enumerate(q2_incrs):
            for j,l in enumerate(lambs):
                # get the frozen positions trajectories:
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
                ax[i,j].plot(df['iter'], Q, color=cons_colors[0], label='Quench')
                axF[i,j].plot(df['iter'], f2, color=freq_colors[0], label='Quench')
                # get the mean field trajectories:
                subprocess.call(f'tar -xzf ../sim_some_params/{model}/time_evos/time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q1+q2_inc}_l_{l}.tar.gz',shell=True)
                for k in range(Navg):
                    df = pd.read_csv(f'time_evo_csv/time_evo_rea_'+str(k+1).zfill(3)+'.csv')
                    if(k==0):
                        Q = np.array(df['f2']-2*df['f1'])
                        f2 = np.array(df['f2'])
                    else:
                        Q += np.array(df['f2']-2*df['f1'])
                        f2 += np.array(df['f2'])
                Q /= Navg
                f2 /= Navg
                ax[i,j].plot(df['iter'], Q, color=cons_colors[1], label='MF')
                axF[i,j].plot(df['iter'], f2, color=freq_colors[1], label='MF')
                # get the deterministic trajectories:
                df = pd.read_csv(f'../deterministic_evolution/results/euler_time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q1+q2_inc}_l_{l}.csv')
                ax[i,j].plot(df['iter'], df['f2']-2*df['f1'], color='k', label='det')
                axF[i,j].plot(df['iter'], df['f2'], color='k', label='det')
                if(i==2 and j==4):
                    handles, labels = ax[i,j].get_legend_handles_labels()
                    handlesF, labelsF = axF[i,j].get_legend_handles_labels()
                if(i==0):
                    ax[i,j].set_title(rf'$\lambda$ = {l}')
                    axF[i,j].set_title(rf'$\lambda$ = {l}')
                if(j==0):
                    ax[i,j].set_ylabel(rf'Q, $\Delta q = {q2_inc}$')
                    axF[i,j].set_ylabel(rf'$f_2$, $\Delta q = {q2_inc}$')
                ax[i,j].set_xscale('log')
                ax[i,j].set_ylim(-0.4,0.8)
                ax[i,j].set_xlim(0.7,5000)
                ax[i,j].grid(axis='y', which='major', color='xkcd:gray', linestyle='-', alpha=0.6)
                ax[i,j].grid(axis='x', which='major', color='xkcd:gray', linestyle='-', alpha=0.6)
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
fig.savefig(f'FPvsMF_time_evos_Qavg_q1_{q1}_q2_plus_{q2_incrs[0]}{q2_incrs[1]}{q2_incrs[2]}_pi1_{pi1}_pi2_{pi2}.png')

figF.legend(handlesF, labelsF, loc='lower right', fontsize='x-large')
figF.tight_layout()
figF.savefig(f'FPvsMF_time_evos_f2avg_q1_{q1}_q2_plus_{q2_incrs[0]}{q2_incrs[1]}{q2_incrs[2]}_pi1_{pi1}_pi2_{pi2}.png')

