# from textwrap import fill # ??
# from turtle import circle, position # ??
from asyncio import subprocess
import numpy as np
import random
from sys import argv
import matplotlib.pyplot as plt
import os
import glob
import subprocess
import sys
sys.path.append('../')
from package_global_functions import getExternalSSDpath

# generate random points in a circular area:
# https://stackoverflow.com/questions/30564015/how-to-generate-random-points-in-a-circular-distribution
# explanation of how the sqrt(random) * arena_r yields a uniform distribution:
# https://stackoverflow.com/questions/5837572/generate-a-random-point-within-a-circle-uniformly


# default_seed
seed = 42

def modifyInput(N_bots, arena_r, exclusion_r, push):
    subprocess.call(f"sed -i 's/^N_bots.*/N_bots = {N_bots}/' input_template_fp.txt", shell=True)
    subprocess.call(f"sed -i 's/^bots_per_site.*/bots_per_site = {N_bots} 0 0/' input_template_fp.txt", shell=True)
    subprocess.call(f"sed -i 's/^arena_r.*/arena_r = {arena_r}/' input_template_fp.txt", shell=True)
    subprocess.call(f"sed -i 's/^exclusion_r.*/exclusion_r = {exclusion_r}/' input_template_fp.txt", shell=True)
    subprocess.call(f"sed -i 's/^push.*/push = {push}/' input_template_fp.txt", shell=True)

if len(argv)==3:
    seed = int(argv[1])
    # Numbers of configurations to generate:
    Nconfigs = int(argv[2])
elif len(argv)==7:
    seed = int(argv[1])
    Nconfigs = int(argv[2])
    N_bots = int(argv[3])
    arena_r = float(argv[4])
    exclusion_r = float(argv[5])
    push = bool(int(argv[6]))
    if push:
        push = ".true."
    else:
        push = ".false."
    modifyInput(N_bots, arena_r, exclusion_r, push)
else:
    seed = int(input('seed: '))
    Nconfigs = int(input('Nconfigs: '))
    N_bots = int(input('Nbots: '))
    arena_r = float(input('Arena radius: '))
    exclusion_r = float(input('Exclusion radius: '))
    push = bool(int(input('Push (0/1): ')))
    if push:
        push = ".true."
    else:
        push = ".false."
    modifyInput(N_bots, arena_r, exclusion_r, push)

random.seed(seed)

file_in = open('input_template_fp.txt', 'r')
file_params = file_in.readlines()
N = int(file_params[11].split('=')[1])
arena_r = float(file_params[39].split('=')[1])
arena_x = float(file_params[40].split('=')[1])
arena_y = float(file_params[41].split('=')[1])
interac_r = float(file_params[42].split('=')[1]) # no need to have it...
exclusion_r = float(file_params[43].split('=')[1])
push = str(file_params[44].split('=')[1]).strip()
file_in.close()

if(push == ".true."):
    push_folder = "configs_w_push"
    pushFlag = True
else:
    push_folder = "configs_wo_push"
    pushFlag = False
    
effectiveArena_r = arena_r-exclusion_r

# # random angle:
# alpha = 2 * np.pi * random.random()
# # random radius:
# r = arena_r * np.sqrt(random.random())
# # x,y coordinates:
# x = r * np.cos(alpha) + arena_x
# y = r * np.sin(alpha) + arena_y

# print("Random point", (x,y))

def distance(pos1,pos2):
    return np.sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)

def push(pos_to_move,pos_fixed):
    vector = (pos_to_move[0]-pos_fixed[0], pos_to_move[1]-pos_fixed[1])
    factor = 2*exclusion_r-distance(pos_to_move,pos_fixed)
    new_position = (pos_to_move[0]+factor*vector[0], pos_to_move[1]+factor*vector[1])
    inside = True
    if(sum([coor**2 for coor in new_position]) > effectiveArena_r**2):
        # position after push lays out of the arena, discard it
        inside = False
    return new_position, inside

def checkDistNeighbors(bot_id,pos_bot):
    for i in range(bot_id):
        if distance(pos_bot,positions[i]) < 2*exclusion_r:
            return False, i
    return True, 0

def plotConfiguration(failed_position=False):
    fig, ax = plt.subplots()
    circle = plt.Circle([arena_x, arena_y], arena_r, fill=False, edgecolor='k')
    ax.add_patch(circle)
    ax.set_xlim(-(arena_r+1),arena_r+1)
    ax.set_ylim(-(arena_r+1),arena_r+1)
    plt.axis('off')
    for i,pos in enumerate(positions):
        # https://stackoverflow.com/questions/1320731/count-number-of-files-with-certain-extension-in-python
        configCounter = len(glob.glob(f'positions_and_contacts/{N}_bots/{push_folder}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'))
        ofName = f'img_bots_xy_positions_{str(configCounter).zfill(3)}_ar_{arena_r}_er_{exclusion_r}.png'
        circle = plt.Circle(tuple(pos), exclusion_r, color='xkcd:purple', alpha=0.8, clip_on=False)
        ax.add_patch(circle)
        ax.scatter(pos[0], pos[1], color='xkcd:purple')
    if(failed_position):
        configCounter = len(glob.glob(f'positions_and_contacts/{N}_bots/{push_folder}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}_failed.png'))
        ofName = f'img_bots_xy_positions_{str(configCounter).zfill(3)}_ar_{arena_r}_er_{exclusion_r}_failed.png'
        circle = plt.Circle(failed_position, exclusion_r, color='xkcd:black', alpha=0.5, clip_on=False)
        ax.add_patch(circle)
    fig.text(0.2,0.9, rf"$r_a = {arena_r}, \; r_e = {exclusion_r}$")
    fig.savefig(ofName)
    subprocess.call(f'mv {ofName} positions_and_contacts/{N}_bots/{push_folder}', shell=True)

def writeConfiguration():
    subprocess.call(f'mkdir -p positions_and_contacts/{N}_bots/{push_folder}', shell=True)
    configCounter = len(glob.glob(f'positions_and_contacts/{N}_bots/{push_folder}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'))
    ofName = f'bots_xy_positions_{str(configCounter+1).zfill(3)}_ar_{arena_r}_er_{exclusion_r}.txt'
    wf = open(ofName, 'w')
    for i in range(N):
        wf.write(f"{i+1:3d} {positions[i][0]:13.8f} {positions[i][1]:13.8f}\n")
    wf.close()
    subprocess.call(f'mv {ofName} positions_and_contacts/{N}_bots/{push_folder}', shell=True)
    
def generateConfiguration(pushFlag=True):
    positions.clear()
    max_attempts_per_bot = 150
    max_push_attempts_per_bot = N
    for i in range(N):
        positionAccepted = False
        count_attempts = 0
        while not positionAccepted and count_attempts < max_attempts_per_bot:
            count_attempts += 1
            alpha = 2 * np.pi * random.random()
            r = effectiveArena_r * np.sqrt(random.random())
            x = r * np.cos(alpha) + arena_x
            y = r * np.sin(alpha) + arena_y
            new_pos_bot = [x,y]
            positionAccepted, overlapped_bot = checkDistNeighbors(i,new_pos_bot)
            # if initial position is not accepted, try pushing the bot to avoid overlap
            if not positionAccepted and pushFlag:
                count_push_attempts = 0
                while not positionAccepted and count_push_attempts < max_push_attempts_per_bot:
                    count_push_attempts += 1
                    new_pos_bot, inside = push(new_pos_bot,positions[overlapped_bot])
                    if not inside:
                        break
                    positionAccepted, overlapped_bot = checkDistNeighbors(i,new_pos_bot)
        if not positionAccepted:
            print(f"Bot {i} couldn't find a position. Configuration discarded.")
            break
        else:
            positions.append(new_pos_bot)
    # once the configuration is generated, save it to a file
    if(len(positions)==N):
        writeConfiguration()
        #if len(glob.glob(f'positions_and_contacts/{N}_bots/{push_folder}/img_bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.png'))<10:
        #    plotConfiguration()
        return True
    else:
        #plotConfiguration(new_pos_bot)
        return False


completedConfigsCounter = 0
for _ in range(Nconfigs):
    positions = []
    completed = generateConfiguration(pushFlag=pushFlag)
    if completed : completedConfigsCounter +=1
    
print(f'Successfuly generated {completedConfigsCounter} configurations from the {Nconfigs} required.')

# COPY CONFIGURATIONS TO EXTERNAL SSD
ssdpath = getExternalSSDpath()
if ssdpath:
    subprocess.call(f'mkdir -p {ssdpath}/quenched_configs/{N}_bots/{push_folder}/', shell=True)
    subprocess.call(f'cp positions_and_contacts/{N}_bots/{push_folder}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt {ssdpath}/quenched_configs/{N}_bots/{push_folder}/', shell=True)



