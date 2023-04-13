# from textwrap import fill # ??
# from turtle import circle, position # ??
from asyncio import subprocess
import numpy as np
import random
from sys import argv
import argparse
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


def modifyInput(N_bots, arena_r, exclusion_r, push):
    subprocess.call(f"sed -i 's/^N_bots.*/N_bots = {N_bots}/' input_template_fp.txt", shell=True)
    subprocess.call(f"sed -i 's/^bots_per_site.*/bots_per_site = {N_bots} 0 0/' input_template_fp.txt", shell=True)
    subprocess.call(f"sed -i 's/^arena_r.*/arena_r = {arena_r}/' input_template_fp.txt", shell=True)
    subprocess.call(f"sed -i 's/^exclusion_r.*/exclusion_r = {exclusion_r}/' input_template_fp.txt", shell=True)
    subprocess.call(f"sed -i 's/^push.*/push = {push}/' input_template_fp.txt", shell=True)

parser = argparse.ArgumentParser()
parser.add_argument('N_bots', type=int, help='number of bots in the arena')
parser.add_argument('arena_r', type=float, help='radius of the arena')
parser.add_argument('exclusion_r', type=float, help='radius of the agents body')
parser.add_argument('push', type=int, help='generate configs w/wo push (1/0)')
parser.add_argument('seed', type=int, help='seeeeeeeed')
parser.add_argument('N_configs', type=int, help='How many configs to generate')

args = parser.parse_args()
N_bots, arena_r, exclusion_r, push, seed, N_configs = args.N_bots, args.arena_r, args.exclusion_r, args.push, args.seed, args.N_configs

if push == 0:
    pushFortran = '.false.' # for the fortran input
    pushFolder = 'configs_wo_push'
else: # any push different from 0 is push.
    pushFortran = '.true.'
    pushFolder = 'configs_w_push'

modifyInput(N_bots, arena_r, exclusion_r, pushFortran)
random.seed(seed)
effectiveArena_r = arena_r-exclusion_r
ssdpath = getExternalSSDpath()
configsPath = ssdpath + f'/quenched_configs/{N_bots}_bots/{pushFolder}'

def positionFilename(index):
    if index == 0:
        return f'bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'
    else:
        return f'bots_xy_positions_{str(index).zfill(3)}_ar_{arena_r}_er_{exclusion_r}.txt'

# reads arena_x,y centers, but they are always (0,0) and this should never change...
file_in = open('input_template_fp.txt', 'r')
file_params = file_in.readlines()
arena_x = float(file_params[40].split('=')[1])
arena_y = float(file_params[41].split('=')[1])
file_in.close()
    
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

def checkDistNeighbors(bot_id, pos_bot, positions):
    for i in range(bot_id):
        if distance(pos_bot,positions[i]) < 2*exclusion_r:
            return False, i
    return True, 0

# needs rework
def plotConfiguration(failed_position=False):
    fig, ax = plt.subplots()
    circle = plt.Circle([arena_x, arena_y], arena_r, fill=False, edgecolor='k')
    ax.add_patch(circle)
    ax.set_xlim(-(arena_r+1),arena_r+1)
    ax.set_ylim(-(arena_r+1),arena_r+1)
    plt.axis('off')
    for i,pos in enumerate(positions):
        # https://stackoverflow.com/questions/1320731/count-number-of-files-with-certain-extension-in-python
        configCounter = len(glob.glob(f'positions_and_contacts/{N_bots}_bots/{pushFolder}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}.txt'))
        ofName = f'img_bots_xy_positions_{str(configCounter).zfill(3)}_ar_{arena_r}_er_{exclusion_r}.png'
        circle = plt.Circle(tuple(pos), exclusion_r, color='xkcd:purple', alpha=0.8, clip_on=False)
        ax.add_patch(circle)
        ax.scatter(pos[0], pos[1], color='xkcd:purple')
    if(failed_position):
        configCounter = len(glob.glob(f'positions_and_contacts/{N_bots}_bots/{pushFolder}/bots_xy_positions_*_ar_{arena_r}_er_{exclusion_r}_failed.png'))
        ofName = f'img_bots_xy_positions_{str(configCounter).zfill(3)}_ar_{arena_r}_er_{exclusion_r}_failed.png'
        circle = plt.Circle(failed_position, exclusion_r, color='xkcd:black', alpha=0.5, clip_on=False)
        ax.add_patch(circle)
    fig.text(0.2,0.9, rf"$r_a = {arena_r}, \; r_e = {exclusion_r}$")
    fig.savefig(ofName)
    subprocess.call(f'mv {ofName} positions_and_contacts/{N_bots}_bots/{pushFolder}', shell=True)

def writeConfiguration(positions, configCounter):
    subprocess.call(f'mkdir -p {configsPath}', shell=True)
    ofName = positionFilename(configCounter)
    wf = open(ofName, 'w')
    for i in range(N_bots):
        wf.write(f"{i+1:3d} {positions[i][0]:13.8f} {positions[i][1]:13.8f}\n")
    wf.close()
    subprocess.call(f'mv {ofName} {configsPath}', shell=True)
    
def generateConfiguration(pushFlag=True):
    positions = []
    max_attempts_per_bot = 150
    max_push_attempts_per_bot = N_bots
    for i in range(N_bots):
        positionAccepted = False
        count_attempts = 0
        while not positionAccepted and count_attempts < max_attempts_per_bot:
            count_attempts += 1
            alpha = 2 * np.pi * random.random()
            r = effectiveArena_r * np.sqrt(random.random())
            x = r * np.cos(alpha) + arena_x
            y = r * np.sin(alpha) + arena_y
            new_pos_bot = [x,y]
            positionAccepted, overlapped_bot = checkDistNeighbors(i, new_pos_bot, positions)
            # if initial position is not accepted, try pushing the bot to avoid overlap
            if not positionAccepted and pushFlag:
                count_push_attempts = 0
                while not positionAccepted and count_push_attempts < max_push_attempts_per_bot:
                    count_push_attempts += 1
                    new_pos_bot, inside = push(new_pos_bot,positions[overlapped_bot])
                    if not inside:
                        break
                    positionAccepted, overlapped_bot = checkDistNeighbors(i, new_pos_bot, positions)
        if not positionAccepted:
            print(f"Bot {i} couldn't find a position. Configuration discarded.")
            break
        else:
            positions.append(new_pos_bot)
    # once the configuration is generated, return
    if(len(positions)==N_bots):
        return positions, True
    else:
        #plotConfiguration(new_pos_bot)
        return positions, False


# check the number of configurations already existing (in the SSD!):
if os.path.exists(configsPath):
    existingConfigs = len(glob.glob(configsPath+f'/{positionFilename(0)}'))
else:
    existingConfigs = 0

print(f'There are already {existingConfigs} configurations generated with these parameters. \n \
      Generating {N_configs} more.')

completedConfigsCounter = 0
for i in range(N_configs):
    positions, completed = generateConfiguration(pushFlag=bool(push))
    if completed:
        writeConfiguration(positions, existingConfigs+completedConfigsCounter+1)
        completedConfigsCounter +=1
    
print(f'Successfuly generated {completedConfigsCounter} configurations from the {N_configs} required.')


