# contact_list_*.txt is generated when executing simulations
# sometimes, it's convenient to get this files without running whole simulations
# this code is used to run 'fake' simulations of duration=1 to get this files

from sys import argv
import argparse
from subprocess import call
import glob
import os
import sys
sys.path.append('../')
from package_global_functions import getExternalSSDpath


# argumetnts to recieve: N_bots arena_r interac_r exclusion_r push
parser = argparse.ArgumentParser()
parser.add_argument('N_bots', type=int, help='number of bots in the arena')
parser.add_argument('arena_r', type=float, help='radius of the arena')
parser.add_argument('interac_r', type=float, help='radius of interaction')
parser.add_argument('exclusion_r', type=float, help='radius of the agents body')
parser.add_argument('push', type=int, help='generate configs w/wo push (1/0)')
parser.add_argument('-ow', '--overwrite', help='Overwrite contacts even having been generated after configs', action='store_true')

# for the moment I program so the contacts of all configurations are generated, even if they already exist
# in the future I could implement so I specify to generate all/non_existing(+contacts older than positions, if positions have been regenerated for some reason)
# parser.add_argument('N_configs', type=int, help='How many configs to generate')

args = parser.parse_args()
N_bots, arena_r, interac_r, exclusion_r, push = args.N_bots, args.arena_r, args.interac_r, args.exclusion_r, args.push

if push == 0:
    pushFortran = '.false.' # for the fortran input
    pushFolder = 'configs_wo_push'
else: # any push different from 0 is push.
    pushFortran = '.true.'
    pushFolder = 'configs_w_push'

max_time = 1

ssdpath = getExternalSSDpath()
configsPath = ssdpath + f'/quenched_configs/{N_bots}_bots/{pushFolder}'

def positionFilename(index):
    if index == 0:
        return f'bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'
    else:
        return f'bots_xy_positions_{str(index).zfill(3)}_ar_{arena_r}_er_{exclusion_r}.txt'
    
def contactFilename(index):
    if index == 0:
        return f'contact_list_*_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'
    else:
        return f'contact_list_{str(index).zfill(3)}_ar_{arena_r}_er_{exclusion_r}_ir_{interac_r}.txt'
    
configs = glob.glob(f'{configsPath}/{positionFilename(0)}')
contacts = glob.glob(f'{configsPath}/{contactFilename(0)}')
confNeedsContact = 0 # if it remains 0, all configs have their contact already generated, so stop execution
N_configs = len(configs)
N_contacts = len(contacts)

if len(contacts) == len(configs): # check if every contact list is already up to date with every config position
    for conf,cont in zip(configs, contacts):
        if os.path.getmtime(conf) > os.path.getmtime(cont):
            confNeedsContact += 1
else:
    confNeedsContact = 1 # there are no contacts or not as much as configs. Overwrite existing and generate non existing ones.
        
if confNeedsContact == 0 and not args.overwrite:
    sys.exit(0)


print(f'There are {N_configs} position files and {N_contacts} contact files for these parameters. \n \
      Generating {N_configs} contact files.')

# make replacements in fortran input
fin_file = 'input_template_fp.txt'
f_file = 'main_fp.f90'
fex_file = 'main.x'
call(f"sed -i 's/^N_bots.*/N_bots = {N_bots}/' "+fin_file, shell=True)
call(f"sed -i 's/^bots_per_site.*/bots_per_site = {N_bots} 0 0/' "+fin_file, shell=True)
call(f"sed -i 's/^arena_r.*/arena_r = {arena_r}/' "+fin_file, shell=True)
call(f"sed -i 's/^interac_r.*/interac_r = {interac_r}/' "+fin_file, shell=True)
call(f"sed -i 's/^exclusion_r.*/exclusion_r = {exclusion_r}/' "+fin_file, shell=True)
call(f"sed -i 's/^push = .*/push = {pushFortran}/' "+fin_file, shell=True)

call(f"sed -i 's/^max_time.*/max_time = {max_time}/' "+fin_file, shell=True)
call("sed -i 's/ call execute_command_line(\"python stationary_results.py F\")/ !call execute_command_line(\"python stationary_results.py F\")/' "+f_file, shell=True)
call("make", shell=True)
call("./"+fex_file+f" 1 {N_configs}", shell=True)

# restore stationary_results.py
call("sed -i 's/ !call execute_command_line(\"python stationary_results.py F\")/ call execute_command_line(\"python stationary_results.py F\")/' "+f_file, shell=True)
call("make", shell=True)
# reset max_time to an appropiate simulation time
call(f"sed -i 's/max_time.*/max_time = 5000/' "+fin_file, shell=True)



# By default, the fortran program moves the contact files to positions_and_contacts/N_bots/pushFolder/'
# move the contact lists to the external SSD

call(f'mv positions_and_contacts/{N_bots}_bots/{pushFolder}/{contactFilename(0)} {configsPath}', shell=True)
call(f'rm -r positions_and_contacts/{N_bots}_bots/', shell=True)
