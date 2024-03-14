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

# Read all the output trajectories and put them in df_list
def file_id(i):
    if 1 <= i <= 9:
        file_id = '00'+str(i)
    elif 10 <= i <= 99:
        file_id = '0'+str(i)
    else:
        file_id = str(i)
    return file_id
    
# Get the N_sites, pis, lambas, qualities from input template txt
rFile = open('input_template_fp.txt', 'r')
for line in rFile.readlines():
    if('N_sites = ' in line):
        N_sites = int(line.split()[2])
    if('lambda = ' in line):
        lamb = float(line.split()[2])
    if('pi(:) = ' in line):
        pi1, pi2 = float(line.split()[2]), float(line.split()[3])
    if('q(:) = ' in line):
        q1, q2 = float(line.split()[2]), float(line.split()[3])
rFile.close()
    
# For the new order parameter, get the stationary results at lambda 1
#def aprox_fs_l1(q1,q2):
#    if(q2>q1):
#        return (1/q2,0.0,1-1/q2)
#    else:
#        return [1/q1,1-1/q1,0.0]
        
#f2_l1 = aprox_fs_l1(q1,q2)[2]

# And at lambda 0
#wd = os.getcwd()
#route0 = '../deterministic_solutions/'
#fex_file = 'main.x'
#fin_file = 'input_template_f0.txt'
# first modifly input_template_f0.txt accordingly
#subprocess.call(f"sed -i 's/N_sites = .*/N_sites = {N_sites}/' "+route0+fin_file, shell=True)
#subprocess.call(f"sed -i 's/lambda = .*/lambda = 0.0/' "+route0+fin_file, shell=True)
#subprocess.call(f"sed -i 's/pi(:) = .*/pi(:) = {pi1} {pi2}/' "+route0+fin_file, shell=True)
#subprocess.call(f"sed -i 's/q(:) = .*/q(:) = {q1} {q2}/' "+route0+fin_file, shell=True)
# the exectue the root finder
#os.chdir(route0)
#subprocess.call("./"+f'{fex_file}', shell=True)
#df0 = pd.read_csv('roots.csv')
#os.chdir(wd)

#f2_l0 = df0.iloc[0]['f2']


num_files = len(os.listdir('time_evo_csv/'))
fs_labels = []
fs = []
#ks = []
for i in range(N_sites+1):
    fs.append([])
    #ks.append([])
    fs_labels.append(f'f{i}')
Q = []
#m = []
# stat_from = 10000
last_iters = 1000
for i in range(1,num_files+1):
    df = pd.read_csv(f'time_evo_csv/time_evo_rea_'+str(i).zfill(3)+'.csv')
    df.drop('iter', axis=1, inplace=True)
    df['m'] = (3*df[fs_labels].max(axis=1)-1)/2
    df['Q'] = df['f2']-2*df['f1']
    for i in range(N_sites+1):
        # fs[i].extend(list(df[f'f{i}'])[stat_from:])
        # ks[i].extend(list(df[f'k{i}'])[stat_from:])
        fs[i].extend(list(df[f'f{i}'])[-last_iters:])
        # ks[i].extend(list(df[f'k{i}'])[-last_iters:])
    # Q.extend(list(df['Q'])[stat_from:])
    # m.extend(list(df['m'])[stat_from:])
    Q.extend(list(df['Q'])[-last_iters:])
    # m.extend(list(df['m'])[-last_iters:])
    
# get the number of bots in the simulation
#rFile = open('input_template.txt', 'r')
#for line in rFile.readlines():
#    if('N_bots=' in line):
#        N_bots = int(line[7:])    
    
# w_file = open('stationary_results.csv', 'w')
# w_file.write('f0,f1,f2,sdf0,sdf1,sdf2,Q,sdQ\n',)
# fs_st = []
# #ks_st = []
# sdfs_st = []
# #sdks_st = []
# for i in range(N_sites+1):
#     fs_st.append(np.array(fs[i]).mean())
#     #ks_st.append(np.array(ks[i]).mean())
#     sdfs_st.append(np.array(fs[i]).std())
#     #sdks_st.append(np.array(ks[i]).std())
# Q_st = np.array(Q).mean()
# sdQ_st = np.array(Q).std()
# #m_st = np.array(m).mean()
# #sdm_st = np.array(m).std()
# #w_file.write(f'{round(fs_st[0],10)},{round(fs_st[1],10)},{round(fs_st[2],10)},{round(sdfs_st[0],10)},{round(sdfs_st[1],10)},{round(sdfs_st[2],10)},{round(Q_st,10)},{round(sdQ_st,10)},{round(m_st,10)},{round(sdm_st,10)},{round(ks_st[0],10)},{round(ks_st[1],10)},{round(ks_st[2],10)},{round(sdks_st[0],10)},{round(sdks_st[1],10)},{round(sdks_st[2],10)}')
# w_file.write(f'{round(fs_st[0],10)},{round(fs_st[1],10)},{round(fs_st[2],10)},{round(sdfs_st[0],10)},{round(sdfs_st[1],10)},{round(sdfs_st[2],10)},{round(Q_st,10)},{round(sdQ_st,10)}')
# w_file.close()



w_file = open('stationary_results.csv', 'w')
# build the csv header:
header = ''
for i in range(N_sites+1):
    header += f'f{i},'
for i in range(N_sites+1):
    header += f'sdf{i},'
# header += 'Q,sdQ,m,sdm,'
header += 'Q,sdQ\n'
# for i in range(N_sites+1):
#     header += f'k{i},'
# for i in range(N_sites):
#     header += f'sdk{i},'
# header += f'sdk{N_sites}'
#w_file.write('f0,f1,f2,sdf0,sdf1,sdf2,Q,sdQ,m,sdm,k0,k1,k2,sdk0,sdk1,sdk2\n',) # two sites fixed format
w_file.write(header)
fs_st = []
# ks_st = []
sdfs_st = []
# sdks_st = []
for i in range(N_sites+1):
    fs_st.append(np.array(fs[i]).mean())
    # ks_st.append(np.array(ks[i]).mean())
    sdfs_st.append(np.array(fs[i]).std())
    # sdks_st.append(np.array(ks[i]).std())
Q_st = np.array(Q).mean()
sdQ_st = np.array(Q).std()
# build the results line:
decimals = 10
results = ''
for i in range(N_sites+1):
    results += f'{round(fs_st[i],decimals)},'
for i in range(N_sites+1):
    results += f'{round(sdfs_st[i],decimals)},'
results += f'{round(Q_st,decimals)},{round(sdQ_st,decimals)}'
# for i in range(N_sites+1):
#     results += f'{round(ks_st[i],decimals)},'
# for i in range(N_sites):
#     results += f'{round(sdks_st[i],decimals)},'
# results += f'{round(sdks_st[N_sites],decimals)}'

w_file.write(results)
    
#w_file.write(f'{round(fs_st[0],10)},{round(fs_st[1],10)},{round(fs_st[2],10)},{round(sdfs_st[0],10)},{round(sdfs_st[1],10)},{round(sdfs_st[2],10)},{round(Q_st,10)},{round(sdQ_st,10)},{round(m_st,10)},{round(sdm_st,10)},{round(ks_st[0],10)},{round(ks_st[1],10)},{round(ks_st[2],10)},{round(sdks_st[0],10)},{round(sdks_st[1],10)},{round(sdks_st[2],10)}')
w_file.close()