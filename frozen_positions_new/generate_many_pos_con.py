from subprocess import call
import numpy as np
import os
import glob
from random import seed, randint
import sys
sys.path.append('../')
from package_global_functions import getExternalSSDpath

seed(7812)
arena_r = 75.0


ssdpath = getExternalSSDpath()

#Ns = {
#    10:np.linspace(5.0, 20.0,16),
#    15:np.linspace(5.0, 17.0,13),
#    20:np.linspace(5.0,14.0,10),
#    25:np.linspace(5.0, 14.0,10),
#    30:np.linspace(5.0, 11.0,13),
#    40:np.linspace(5.0, 10.0,11),
#    50:np.linspace(5.0, 9.0,9),
#    60:np.linspace(5.0, 9.0,9),
#    70:np.linspace(5.0, 9.0,9),
#    80:np.linspace(5.0, 9.0,9)
#}

# around the peak or extras
#Ns = {
#    10:[4.0, ],
#    15:[4.0, ],
#    20:[4.0, ],
#    25:[4.0, ],
#    30:[4.0, ],
#    40:[4.0, ],
    # 50:[4.2, 4.4, 4.6, 4.8],
    # 60:[4.2, 4.4, 4.6, 4.8],
    # 70:[3.5, 3.6, 3.8, 4.2, 4.4, 4.6, 4.8],
    # 80:[3.5, 3.6, 3.8, 4.0, 4.2, 4.4, 4.5, 4.6 , 4.8]
#}

Ns = {
    352:np.linspace(5.0, 14.0,10),
    703:np.linspace(4.0, 9.0,11),
    984:np.linspace(3.5, 8.0,10)
}

maxConfigs = 250

for N,irs in Ns.items():
    # check the number of configurations already existing (in the SSD!):
    configsPath = ssdpath + f'/quenched_configs/{N}_bots/configs_wo_push'
    if os.path.exists(configsPath):
        existingConfigs = len(glob.glob(configsPath+f'/bots_xy_positions_*_ar_20.0_er_1.5.txt'))
    else:
        existingConfigs = 0
    call(f'python generate_frozen_positions.py {N} {arena_r} 1.5 0 {randint(0,100000)} {maxConfigs-existingConfigs}', shell=True)
    for ir in irs:
        call(f'python generate_contact_list.py {N} {arena_r} {ir} 1.5 0', shell=True)
