import pandas as pd
from sys import argv
from random import seed, randint
from subprocess import call
import os
import numpy as np
from collections import Counter

wd = os.getcwd()

if len(argv)==1:
    inSeed = int(input("Enter SEED: "))
else:
    inSeed = int(argv[1])

# conditions to simulate in order to get positions:
# pis, qs, lambda whatever
N_bots = 35
max_time = 1
arena_r = 20
interac_r = 45
N_rea = 500
seed(inSeed)

# dfavg = pd.DataFrame(columns=['bot_id','degree'])
bot_ids = [i for i in range(1,N_bots+1)]
bot_degrees = [0] * N_bots
bot_degrees = np.array(bot_degrees)
all_degrees = []


# input to Fortran code route:
froute = "/home/david/Desktop/Uni_code/TFM_code/frozen_positions/"
fin_file = 'input_template_fp.txt'
fex_file = 'main.x'
f_file = 'main_fp.f90'

# make all the necesary replacements:
call(f"sed -i 's/^N_bots.*/N_bots = {N_bots}/' "+froute+fin_file, shell=True)
call(f"sed -i 's/^bots_per_site.*/bots_per_site = {N_bots} 0 0/' "+froute+fin_file, shell=True)
call(f"sed -i 's/^max_time.*/max_time = {max_time}/' "+froute+fin_file, shell=True)
call(f"sed -i 's/^arena_r.*/arena_r = {arena_r}/' "+froute+fin_file, shell=True)
call(f"sed -i 's/^interac_r.*/interac_r = {interac_r}/' "+froute+fin_file, shell=True)

# Change to the Fortran code directory and execute
os.chdir(froute)
# stop simulation code from getting stationary results in order to avoid errors (in the .py) due to short simulation times
call("sed -i 's/ call execute_command_line(\"python stationary_results.py F\")/ !call execute_command_line(\"python stationary_results.py F\")/' "+f_file, shell=True)
call("make", shell=True)
call("./"+fex_file+f" {randint(0,100000000)} {N_rea}", shell=True)
# restore stationary_results.py
call("sed -i 's/ !call execute_command_line(\"python stationary_results.py F\")/ call execute_command_line(\"python stationary_results.py F\")/' "+f_file, shell=True)
call("make", shell=True)
# reset max_time to an appropiate simulation time
call(f"sed -i 's/max_time.*/max_time = 5000/' "+fin_file, shell=True)
# read the bot degree files
call("tar -xzf positions_and_contacts.tar.gz", shell=True)
for i in range(N_rea):
    df = pd.read_csv('positions_and_contacts/bot_degree_'+str(i+1).zfill(3)+'.csv')
    bot_degrees += df['degree']
    all_degrees += list(df['degree'])
os.chdir(wd)


degree_counts = len(all_degrees)
degree_counter = Counter(all_degrees)
all_degrees.clear()
probs = []
for k,v in degree_counter.items():
    all_degrees.append(k)
    probs.append(round(v/degree_counts,8))

df_degree_prob = pd.DataFrame({'degree':all_degrees, 'prob':probs})
df_degree_prob.sort_values(by='degree', ignore_index=True, inplace=True)

outputCSV_degree_prob = f"Galla/{N_bots}_bots/degree_probs/degree_probs_ar_{arena_r}_ir_{interac_r}.csv"
df_degree_prob.to_csv(outputCSV_degree_prob, index=False)


bot_degrees /= N_rea
mean_degree = round(bot_degrees.mean(),8)
std_degree = round(bot_degrees.std(),8)
outputCSV_degree_average = f"Galla/{N_bots}_bots/degree_average.csv"
if(os.path.exists(outputCSV_degree_average)):
    df_old = pd.read_csv(outputCSV_degree_average)
    bool_series = (df_old['arena_r']==arena_r) & (df_old['interac_r']==interac_r)
    if not(df_old.loc[bool_series].empty):
        df_old.drop(df_old.loc[bool_series].index, inplace=True)
    # append the new results to the csv dataframe
    df_out = pd.DataFrame({'arena_r':[arena_r,], 'interac_r':[interac_r], 'mean_degree':[mean_degree,], 'std_degree':[std_degree,]})
    df_old = pd.concat([df_old,df_out],ignore_index=True)
else:
    df_old = pd.DataFrame({'arena_r':[arena_r,], 'interac_r':[interac_r], 'mean_degree':[mean_degree,], 'std_degree':[std_degree,]})

df_old.sort_values(by=['arena_r','interac_r'], ignore_index=True, inplace=True)
df_old.to_csv(outputCSV_degree_average, index=False)




