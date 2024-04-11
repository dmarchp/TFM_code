import pandas as pd
import subprocess
import os
from functools import reduce
import matplotlib.pyplot as plt

N = 100
pi1 = 0.4
pi2 = 0.2
q1 = 7
q2 = 10
l = 0.6

#folder_name = "time_evo_csv"
folder_name = f"time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_N_{N}"

def generate_avg_traj():
    #subprocess.call(f"tar -xzf {folder_name}.tar.gz", shell=True)
    df_files = os.listdir(f'{folder_name}/')
    if('time_evo_avg.csv' in df_files):
        df_files.remove('time_evo_avg.csv')
    if(f'euler_time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv' in df_files):
        df_files.remove(f'euler_time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv')
    if(f'time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_N_{N}.png' in df_files):
        df_files.remove(f'time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_N_{N}.png')
    df_list = []
    for f in df_files:
        df_list.append(pd.read_csv(f'{folder_name}/{f}'))
    df_avg = reduce(lambda a, b: a.add(b, fill_value=0), [df.drop(['iter'], axis=1) for df in df_list])
    df_avg = df_avg/len(df_files)
    df_avg.insert(0, 'iter', df_avg.index)
    df_avg.to_csv('time_evo_avg.csv', index=False) #, index=False
    subprocess.call(f'mv time_evo_avg.csv {folder_name}', shell=True)

def plot_avg_traj():
    fig, ax = plt.subplots()
    dfavg = pd.read_csv(f'{folder_name}/time_evo_avg.csv')
    ax.plot(dfavg['iter'], dfavg['f0'], color='red', alpha=0.7)
    ax.plot(dfavg['iter'], dfavg['f1'], color='green', alpha=0.7)
    ax.plot(dfavg['iter'], dfavg['f2'], color='blue', alpha=0.7)
    dfteo = pd.read_csv(f'{folder_name}/euler_time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv')
    ax.plot(dfteo['iter'], dfteo['f0'], color='red', label=r'$f_0$')
    ax.plot(dfteo['iter'], dfteo['f1'], color='green', label=r'$f_1$')
    ax.plot(dfteo['iter'], dfteo['f2'], color='blue', label=r'$f_2$')
    ax.set_xlabel('iterations')
    ax.set_ylabel(r'$f_i$')
    ax.set_xscale('symlog')
    fig.tight_layout()
    fig.savefig(f'time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_N_{N}.png')
    

def main():
    generate_avg_traj()
    input('enter ')
    plot_avg_traj()
    #subprocess.call(f'tar -czf {folder_name}.tar.gz {folder_name}', shell=True)
    #subprocess.call(f'rm -r {folder_name}', shell=True)
    
if __name__ == '__main__':
    main()
