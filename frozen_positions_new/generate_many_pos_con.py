from subprocess import call
import numpy as np
import os
import glob
from random import seed, randint
import sys
sys.path.append('../')
from package_global_functions import getExternalSSDpath

seed(98904)

ssdpath = getExternalSSDpath()

Ns = {
    10:np.linspace(21.0, 23.0,3),
    15:np.linspace(13.5,17.5,5),
    25:np.linspace(7.5,9.5,3),
    30:np.linspace(6.5,8.5,3),
    40:np.linspace(5.5,7.5,3),
    50:np.linspace(4.5,7.5,4),
    60:[4.5,],
    70:[4.5,],
    80:[4.5,]
}


for N,irs in Ns.items():
    # check the number of configurations already existing (in the SSD!):
    configsPath = ssdpath + f'/quenched_configs/{N}_bots/configs_wo_push'
    if os.path.exists(configsPath):
        existingConfigs = len(glob.glob(configsPath+f'/bots_xy_positions_*_ar_20.0_er_1.5.txt'))
    else:
        existingConfigs = 0
    if existingConfigs > 0:
        call(f'python generate_frozen_positions.py {N} 20.0 1.5 0 {randint(0,100000)} {1000-existingConfigs}', shell=True)
    for ir in irs:
        call(f'python generate_contact_list.py {N} 20.0 {ir} 1.5 0', shell=True)