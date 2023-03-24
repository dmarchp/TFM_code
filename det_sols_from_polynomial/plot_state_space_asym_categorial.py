import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import os
import sys
sys.path.append('../')
from package_global_functions import *

# ideas to improve the colormap:
# https://gist.github.com/jakevdp/8a992f606899ac24b711

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    path = '/res_files'

parser = argparse.ArgumentParser()
parser.add_argument('q1', type=int, help='site 1 quality')
parser.add_argument('q2', type=int, help='site 2 quality')
parser.add_argument('l', type=float, help='interdependence (lambda)')

args = parser.parse_args()
q1, q2, l = args.q1, args.q2, args.l

def consensusType(f0,f1,f2,f0max=0.5):
    '''
    1: strong consensus for site 2
    2: simple consensus for site 2
    3: simple consensus for site 1
    4: strong consensus for site 1
    0: not enough f1+f2 to define a consensus. We set max f0max uncomitted bees.
    '''
    if f0 > f0max:
        qt = 0
    else:
        if f2-2*f1 > 0:
            qt = 1
        elif f2-f1 > 0:
            qt = 2
        elif f1-2*f2 > 0:
            qt = 4
        elif f1 - f2 > 0:
            qt = 3
    return qt

fsMesh = np.load(f'{path}/map_asym_q1_{q1}_q2_{q2}_l_{l}.npz')
consensusType_v = np.vectorize(consensusType, )
qtmesh = consensusType_v(fsMesh['fs'][0],fsMesh['fs'][1], fsMesh['fs'][2])

fig, ax = plt.subplots(figsize=(5.6,4.8))
#im = ax.pcolormesh(fsMesh['x'], fsMesh['y'], qtmesh, cmap=plt.cm.get_cmap('tab20c', 4), shading='nearest')
mycmap = ListedColormap(['xkcd:black', 'xkcd:blue', 'xkcd:green', 'xkcd:orange', 'xkcd:red'])
im = ax.pcolormesh(fsMesh['x'], fsMesh['y'], qtmesh, vmin=0, vmax=4, cmap=mycmap, shading='nearest')
ax.set_xlabel('$\pi_1$')
ax.set_ylabel('$\pi_2$')
cb = fig.colorbar(im, ax=ax, aspect=25, shrink=0.75, pad=0.025)
cb.ax.tick_params(labelsize=9)
# if args.Tline:
#     tline = pd.read_csv(f'{path}/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
#     tline = tline.query('pi2 >= 0.01')
#     ax.plot(tline['pi1'], tline['pi2'], color='xkcd:black', lw=0.7)
ax.set_aspect(1.0)
fig.tight_layout(pad=0.1)
fig.savefig(f'stateSpace_asym_q1_{q1}_q2_{q2}_l_{l}_consenusType.png')