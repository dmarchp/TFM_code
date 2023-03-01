import numpy as np
import pandas as pd
import os
from functools import reduce
from sys import argv
import subprocess

if(len(argv)==2):
    if(argv[1] == 'F'): # script called from inside Fortran code, no need to extract the tar.gz
        pass
else:
    os.system('tar -xzf time_evo_csv.tar.gz')
    
# Get the N_sites, pis, lambas, qualities from input template txt
rFile = open('input_template.txt', 'r')
for line in rFile.readlines():
    if('N_sites = ' in line):
        N_sites = int(line.split()[2])
    if('lambda = ' in line):
        lamb = float(line.split()[2])
    if('pi(:) = ' in line):
        pi1, pi2 = float(line.split()[2]), float(line.split()[3])
    if('q(:) = ' in line):
        q1, q2 = int(line.split()[2]), int(line.split()[3])
rFile.close()

num_files = len(os.listdir('time_evo_csv/'))
fs_labels = []
fs = []
ks = []
for i in range(N_sites+1):
    fs.append([])
    ks.append([])
    fs_labels.append(f'f{i}')
Q = []
m = []
stat_from = 1000
for i in range(1,num_files+1):
    df = pd.read_csv(f'time_evo_csv/time_evo_rea_'+str(i).zfill(3)+'.csv')
    df.drop('iter', axis=1, inplace=True)
    df['m'] = (3*df[fs_labels].max(axis=1)-1)/2
    df['Q'] = df['f2']-2*df['f1']
    for i in range(N_sites+1):
        fs[i].extend(list(df[f'f{i}'])[stat_from:])
        ks[i].extend(list(df[f'k{i}'])[stat_from:])
    Q.extend(list(df['Q'])[stat_from:])
    m.extend(list(df['m'])[stat_from:])

    
w_file = open('stationary_results.csv', 'w')
# build the csv header:
header = ''
for i in range(N_sites+1):
    header += f'f{i},'
for i in range(N_sites+1):
    header += f'sdf{i},'
header += 'Q,sdQ,m,sdm,'
for i in range(N_sites+1):
    header += f'k{i},'
for i in range(N_sites):
    header += f'sdk{i},'
header += f'sdk{N_sites}\n'
#w_file.write('f0,f1,f2,sdf0,sdf1,sdf2,Q,sdQ,m,sdm,k0,k1,k2,sdk0,sdk1,sdk2\n',) # two sites fixed format
w_file.write(header)
fs_st = []
ks_st = []
sdfs_st = []
sdks_st = []
for i in range(N_sites+1):
    fs_st.append(np.array(fs[i]).mean())
    ks_st.append(np.array(ks[i]).mean())
    sdfs_st.append(np.array(fs[i]).std())
    sdks_st.append(np.array(ks[i]).std())
Q_st = np.array(Q).mean()
sdQ_st = np.array(Q).std()
m_st = np.array(m).mean()
sdm_st = np.array(m).std()
# build the results line:
decimals = 10
results = ''
for i in range(N_sites+1):
    results += f'{round(fs_st[i],decimals)},'
for i in range(N_sites+1):
    results += f'{round(sdfs_st[i],decimals)},'
results += f'{round(Q_st,decimals)},{round(sdQ_st,decimals)},{round(m_st,decimals)},{round(sdm_st,decimals)},'
for i in range(N_sites+1):
    results += f'{round(ks_st[i],decimals)},'
for i in range(N_sites):
    results += f'{round(sdks_st[i],decimals)},'
results += f'{round(sdks_st[N_sites],decimals)}'

w_file.write(results)
    
#w_file.write(f'{round(fs_st[0],10)},{round(fs_st[1],10)},{round(fs_st[2],10)},{round(sdfs_st[0],10)},{round(sdfs_st[1],10)},{round(sdfs_st[2],10)},{round(Q_st,10)},{round(sdQ_st,10)},{round(m_st,10)},{round(sdm_st,10)},{round(ks_st[0],10)},{round(ks_st[1],10)},{round(ks_st[2],10)},{round(sdks_st[0],10)},{round(sdks_st[1],10)},{round(sdks_st[2],10)}')
w_file.close()

