# contact_list_*.txt is generated when executing simulations
# sometimes, it's convenient to get this files without running whole simulations
# this code is used to run 'fake' simulations of duration=1 to get this files

from sys import argv
from subprocess import call
import glob
import sys
sys.path.append('../')
from package_global_functions import getExternalSSDpath

# argumetnts to recieve: N_bots arena_r interac_r exclusion_r
if len(argv) == 6:
    N_bots = int(argv[1])
    arena_r = float(argv[2])
    interac_r = float(argv[3])
    exclusion_r = float(argv[4])
    push = bool(int(argv[5]))
else:
    print('Wrong input parameters')
    print(' .py N_bots arena_r interac_r exclusion_r push(0/1)')
    exit()
    
if push:
    push = ".true."
    push_folder = "configs_w_push"
else:
    push = ".false."
    push_folder = "configs_wo_push"
max_time = 1
N_rea = len(glob.glob(f'positions_and_contacts/{N_bots}_bots/{push_folder}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'))

# make replacements in fortran input
fin_file = 'input_template_fp.txt'
f_file = 'main_fp.f90'
fex_file = 'main.x'
call(f"sed -i 's/^N_bots.*/N_bots = {N_bots}/' "+fin_file, shell=True)
call(f"sed -i 's/^bots_per_site.*/bots_per_site = {N_bots} 0 0/' "+fin_file, shell=True)
call(f"sed -i 's/^arena_r.*/arena_r = {arena_r}/' "+fin_file, shell=True)
call(f"sed -i 's/^interac_r.*/interac_r = {interac_r}/' "+fin_file, shell=True)
call(f"sed -i 's/^exclusion_r.*/exclusion_r = {exclusion_r}/' "+fin_file, shell=True)
call(f"sed -i 's/^push = .*/push = {push}/' "+fin_file, shell=True)

call(f"sed -i 's/^max_time.*/max_time = {max_time}/' "+fin_file, shell=True)
call("sed -i 's/ call execute_command_line(\"python stationary_results.py F\")/ !call execute_command_line(\"python stationary_results.py F\")/' "+f_file, shell=True)
call("make", shell=True)
call("./"+fex_file+f" 1 {N_rea}", shell=True)

# restore stationary_results.py
call("sed -i 's/ !call execute_command_line(\"python stationary_results.py F\")/ call execute_command_line(\"python stationary_results.py F\")/' "+f_file, shell=True)
call("make", shell=True)
# reset max_time to an appropiate simulation time
call(f"sed -i 's/max_time.*/max_time = 5000/' "+fin_file, shell=True)



# move the contact lists to the external SSD
ssdpath = getExternalSSDpath()
if ssdpath:
    call(f'mkdir -p {ssdpath}/quenched_configs/{N_bots}_bots/{push_folder}/', shell=True)
    call(f'mv positions_and_contacts/{N_bots}_bots/{push_folder}/contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt {ssdpath}/quenched_configs/{N_bots}_bots/{push_folder}', shell=True)
