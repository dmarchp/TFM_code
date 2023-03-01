import numpy as np
import pandas as pd
import os
from functools import reduce
from sys import argv

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

num_files = len(os.listdir('time_evo_csv/'))
df_list = []
#print(num_files)
for i in range(1,num_files+1):
    df = pd.read_csv(f'time_evo_csv/time_evo_rea_{file_id(i)}.csv')
    df['Q'] = df['f2']-2*df['f1']
    df_list.append(df)
    

# AVERAGED TRAJECTORIES:
df_avg = reduce(lambda a, b: a.add(b, fill_value=0), [df.drop(['iter'], axis=1) for df in df_list])
df_avg = df_avg/num_files
df_sd = reduce(lambda a, b: a.add(b, fill_value=0), [(df.drop(['iter'], axis=1)-df_avg)**2 for df in df_list])
df_sd = np.sqrt(df_sd/(num_files-1))

# Stationary values from the averages trajectories:
w_file = open('stationary_results_old.csv', 'w')
w_file.write('f0,f1,f2,sdf0,sdf1,sdf2,Q,sdQ,m,sdm\n',)
f0_st = df_avg['f0'][1000:].mean()
#sdf0_st = df_avg['f0'][1000:].std()
sdf0_st = df_sd['f0'][1000:].mean()
f1_st = df_avg['f1'][1000:].mean()
#sdf1_st = df_avg['f1'][1000:].std()
sdf1_st = df_sd['f1'][1000:].mean()
f2_st = df_avg['f2'][1000:].mean()
#sdf2_st = df_avg['f2'][1000:].std()
sdf2_st = df_sd['f2'][1000:].mean()
Q_st = f2_st - 2*f1_st
sdQ_st = 2*sdf1_st + sdf2_st # from correlated error propagation
m = (3*max([f0_st, f1_st, f2_st])-1)/2
sdm = 0
#print(f"Average f0: {round(f0_st,4)} +- {round(sdf0_st,4)}")
#print(f"Average f1: {round(f1_st,4)} +- {round(sdf1_st,4)}")
#print(f"Average f2: {round(f2_st,4)} +- {round(sdf2_st,4)}")
#print(f"Average Q: {round(Q_st,4)} +- {round(sdQ_st,4)}")
w_file.write(f'{f0_st},{f1_st},{f2_st},{sdf0_st},{sdf1_st},{sdf2_st},{Q_st},{sdQ_st},{m},{sdm}')
w_file.close()
# Stationary consensus value from computing the consensus along the trajectory
#print(f"Average Q: {round(df_avg['Q'][1000:].mean(),4)} +- {round(df_avg['Q'][1000:].std(),4)}")
#print(f"Average Q: {df_avg['Q'][1000:].mean()} +- {df_avg['Q'][1000:].std()}")
