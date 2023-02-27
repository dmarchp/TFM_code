import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sys import argv

if(len(argv)==6):
    pi1, pi2 = float(argv[1]), float(argv[2])
    q1, q2 = int(argv[3]), int(argv[4])
    l = float(argv[5])
else:
    pi1 = float(input("Enter discovery prob for site 1: "))
    pi2 = float(input("Enter discovery prob for site 2: "))
    q1 = int(input("Enter quality of site 1: "))
    q2 = int(input("Enter quality of site 2: "))
    l = float(input("Enter the interdependence :"))

#q1=2
#q2=3
#l=0.6
#pi1=0.1
#pi2=0.1

model_folder = 'Galla/'
#model_folder = 'List/'

# Read different trajectories and combine them:
stat_values = []
subprocess.call(f'tar -xzf {model_folder}time_evos/time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.tar.gz',shell=True)
for i in range(20):
    #df = pd.read_csv(f'time_evo_csv/time_evo_rea_00'+str(i+1)+'.csv')
    df = pd.read_csv(f'time_evo_csv/time_evo_rea_'+str(i+1).zfill(3)+'.csv')
    df.drop(df[df.iter < 500].index, inplace=True)
    df.drop(df[df.iter > 5000].index, inplace=True)
    df.drop('iter', axis=1, inplace=True)
    for j,col in enumerate(df):
        if(i==0):
            stat_values.append(list(df[col]))
        else:
            for val in list(df[col]):
                stat_values[j].append(val)

df_stat = pd.DataFrame({'f0':stat_values[0], 'f1':stat_values[1], 'f2':stat_values[2]})

subprocess.call(f'mkdir -p {model_folder}stationary_dfs/', shell=True)
df_stat.to_csv(f'stat_values_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv')
subprocess.call(f'mv stat_values_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}.csv {model_folder}stationary_dfs/', shell=True)


# BOX & WHISKERS PLOT

#fig, ax = plt.subplots()
#ax = sns.boxplot(data=df)
#ax.artists[0].set_color('red')
#ax.artists[1].set_color('green')
#ax.artists[2].set_color('blue')
#for i in range(len(ax.lines[:])):
#    ax.lines[i].set_color('black')
#for i in range(3):
#    ax.artists[i].set_edgecolor('black')
#plt.savefig('prova_bw.png')
#plt.clf()


# HISTOGRAM

#fig, ax = plt.subplots()
#ax = sns.displot(df['f2'], bins=25)
#ax = sns.displot(df['f1'], bins=25)
#sns.histplot(df['f2'], bins=20, color='b')
#sns.histplot(df['f1'], bins=20, color='r')
#plt.savefig('prova_histo.png')


subprocess.call('rm -r time_evo_csv', shell=True)

