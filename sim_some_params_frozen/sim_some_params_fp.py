from sys import argv
import subprocess
import os
import pandas as pd
from random import seed, randint
from tqdm import tqdm

if len(argv)==1:
    inSeed = int(input("Enter SEED: "))
    #model = input("Simulate List or Galla? (List/Galla or L/G) ")
else:
    inSeed = int(argv[1])
    #model = str(argv[2])
    
model = 'Galla'
seed(inSeed)
num_rea = 100

# All the parameters to simulate:

# radii
push = ".false."
arena_r = 20.0
#interac_r = [10.0, 8.0, 3.0]
interac_r = [4.2, 4.5, 4.8]
exclusion_r = 1.5
#interac_r = [20,13,12,11,10,9,8,7,6,5,4,3,2,1]
#interac_r = [20,12,10,7,4,3,2]
#interac_r = [11,9,8,6,5]

# qualities, pis, lambdas
q1s = [7, ]
q2s = [10, ]
lambs = []
#for i in range(0,100,10):
#    lambs.append(i/100)
for i in range(0,100,5):
    lambs.append(i/100)
pi1s = [0.3, ]
pi2s = [0.3, ]

# Number of bots
N_bots = 35

wd = os.getcwd()
# input to Fortran code route:
froute = "/home/david/Desktop/Uni_code/TFM_code/frozen_positions_new/"
fin_file = 'input_template_fp.txt'
fex_file = 'main.x'
f_file = 'main_fp.f90'

#if model in ["G", "Galla", "galla"]:
#    subprocess.call("sed -i 's/ !call update_system_galla()/ call_update_system_galla()/' "+froute+f_file, shell=True)
#    subprocess.call("sed -i 's/ call update_system()/ !call update_system()/' "+froute+f_file, shell=True)
#    model = "Galla" # make sure that first letter is capitalized
#elif model in ["L", "List", "list"]:
#    subprocess.call("sed -i 's/ call update_system_galla()/ !call update_system_galla()/' "+froute+f_file, shell=True)
#    subprocess.call("sed -i 's/ !call update_system()/ call update_system()/' "+froute+f_file, shell=True)
#    model = "List"
#else:
#    print("Incorrect model introduced, shuting down!")
#    exit()
#os.chdir(froute)
#subprocess.call('make', shell=True)
#os.chdir(wd)

subprocess.call(f"mkdir -p {model}/{N_bots}_bots/", shell=True)
subprocess.call(f"sed -i '12s/.*/N_bots = {N_bots}/' "+froute+fin_file, shell=True)
subprocess.call(f"sed -i '35s/.*/bots_per_site = {N_bots} 0 0/' "+froute+fin_file, shell=True)


subprocess.call(f"sed -i 's/arena_r.*/arena_r = {arena_r}/' "+froute+fin_file, shell=True)
# subprocess.call(f"sed -i 's/interac_r.*/interac_r = {interac_r}/' "+froute+fin_file, shell=True)
subprocess.call(f"sed -i 's/exclusion_r.*/exclusion_r = {exclusion_r}/' "+froute+fin_file, shell=True)
subprocess.call(f"sed -i 's/^push =.*/push = {push}/' "+froute+fin_file, shell=True)


# OUTPUT DATA FRAME:
if(push == ".false."):
    of_name = f'{model}/{N_bots}_bots/sim_fp_results_er_{exclusion_r}_NOPUSH.csv'
else:
    of_name = f'{model}/{N_bots}_bots/sim_fp_results_er_{exclusion_r}.csv'

df_out = pd.DataFrame(columns=['arena_r','interac_r','pi1','pi2','q1','q2','lambda','f0','f1','f2','sdf0','sdf1','sdf2','Q','sdQ','m','sdm','k0','k1','k2','sdk0','sdk1','sdk2'])

#for pi1 in tqdm(pi1s):
for pi1 in pi1s:
    for pi2 in pi2s:
        subprocess.call(f"sed -i '27s/.*/pi(:) = {pi1} {pi2}/' "+froute+fin_file, shell=True)
        for q1 in q1s:
            for q2 in q2s:
                subprocess.call(f"sed -i '30s/.*/q(:) = {q1} {q2}/' "+froute+fin_file, shell=True)
                for l in tqdm(lambs):
                    subprocess.call(f"sed -i '17s/.*/lambda = {l}/' "+froute+fin_file, shell=True)
                    for ir in interac_r:
                        subprocess.call(f"sed -i 's/interac_r.*/interac_r = {ir}/' "+froute+fin_file, shell=True)
                        # Change to the Fortran code directory and execute
                        os.chdir(froute)
                        subprocess.call("./"+fex_file+f" {randint(0,100000000)} {num_rea}", shell=True)
                        os.chdir(wd)
                        # Get the average values from the execution:
                        df = pd.read_csv(froute+'stationary_results.csv')
                        df.insert(0,'lambda',l)
                        df.insert(0,'q2',q2)
                        df.insert(0,'q1',q1)
                        df.insert(0,'pi2',pi2)
                        df.insert(0,'pi1',pi1)
                        # df.insert(0,'interac_r', interac_r)
                        df.insert(0,'interac_r', ir)
                        df.insert(0,'arena_r', arena_r)
                        df_out = pd.concat([df_out,df])
                        # Get the time evolutions
                        #subprocess.call(f"mkdir -p {model}/{N_bots}_bots/time_evos/", shell=True)
                        #subprocess.call(f"cp ../frozen_positions/time_evo_csv.tar.gz {model}/{N_bots}_bots/time_evos/", shell=True)
                        #subprocess.call(f"mv {model}/{N_bots}_bots/time_evos/time_evo_csv.tar.gz {model}/{N_bots}_bots/time_evos/time_evo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_ar_{arena_r}_ir_{interac_r}.tar.gz", shell=True)
                    
# if a param combination was already simulated&stored in the csv, /overwritte it/ delete it and append from the new data
if(os.path.exists(of_name)):
    df_old = pd.read_csv(of_name)
    for index,row in df_out.iterrows():
        bool_series = (df_old['arena_r']==row['arena_r']) & (df_old['interac_r']==row['interac_r']) & (df_old['pi1']==row['pi1']) & (df_old['pi2']==row['pi2']) & (df_old['q1']==row['q1']) & (df_old['q2']==row['q2']) & (df_old['lambda']==row['lambda'])
        if not(df_old.loc[bool_series].empty):
            df_old.drop(df_old.loc[bool_series].index,inplace=True)
    # append the new results to the csv dataframe
    df_old = pd.concat([df_old,df_out],ignore_index=True)
else:
    df_old = df_out
    
df_old = df_old.sort_values(by=['arena_r','interac_r','pi1','pi2','q1','q2','lambda'], ignore_index=True)

# finally write the csv again (overwrite the previously existing for it's now updated and/or enlarged)
df_old.to_csv(of_name, index=False)
