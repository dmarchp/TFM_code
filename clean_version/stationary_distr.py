import pandas as pd
import subprocess
import os
from functools import reduce
import matplotlib.pyplot as plt

pi1 = 0.4
pi2 = 0.2
q1 = 7
q2 = 10
l = 0.6
N_list = [35, 100, 500]

def plot_stationary_distr(N_list):
    fig, ax = plt.subplots()
    ax.set_xlabel(r'$f_2$')
    ax.set_ylabel('Counts')
    fig.text(0.1,0.97, rf"$(\pi_1, \pi_2) = ({pi1}, {pi2}), \; (q_1, q_2) = ({q1}, {q2}), \; \lambda = {l}$", fontsize=10)
    for N in N_list:
        folder_name = f"time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_N_{N}"
        df_files = os.listdir(f'{folder_name}/')
        if('time_evo_avg.csv' in df_files):
            df_files.remove('time_evo_avg.csv')
        if(f'euler_time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv' in df_files):
            df_files.remove(f'euler_time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv')
        if(f'time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_N_{N}.png' in df_files):
            df_files.remove(f'time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_N_{N}.png')
        f2s = []
        for f in df_files:
            df = pd.read_csv(f'{folder_name}/{f}')
            f2s.extend(list(df['f2'][500:]))
        ax.hist(f2s, label=f'{N}', alpha=0.4)
    fig.legend()
    fig.tight_layout()
    fig.savefig(f'stationary_distr_f2_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_N_{N}.png')
        
def main():
    plot_stationary_distr(N_list)



if __name__ == '__main__':
    main()
