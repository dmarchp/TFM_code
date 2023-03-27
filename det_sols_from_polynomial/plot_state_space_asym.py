# plot the phase space + Tline for a specific lambda
import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    path = '/res_files'

parser = argparse.ArgumentParser()
parser.add_argument('q1', type=int, help='site 1 quality')
parser.add_argument('q2', type=int, help='site 2 quality')
parser.add_argument('l', type=float, help='interdependence (lambda)')
parser.add_argument(
    'x', type=float, help='factor between f1 and f2, f2 = x*f1')
parser.add_argument('-mask', help='mask the upper trigangle where pi1+pi2 > 1', action='store_true')
parser.add_argument('-Tline', help='Add theoretical transition line to the colormap plot', action='store_true')
args = parser.parse_args()

q1, q2, l, x = args.q1, args.q2, args.l, args.x

fsMesh = np.load(f'{path}/map_asym_q1_{q1}_q2_{q2}_l_{l}.npz')
Qmesh = fsMesh['fs'][2] - x*fsMesh['fs'][1]
sumXY = fsMesh['x'] + fsMesh['y']

if args.mask:
    # empty = np.empty(Qmesh.shape)
    # empty[:] = np.nan
    zeros = np.zeros(Qmesh.shape)
    Qmesh_masked = np.where(sumXY > 1, zeros, Qmesh)
    Qmesh = Qmesh_masked

max = abs(Qmesh).max()

fig, ax = plt.subplots(figsize=(5.6,4.8))
im = ax.pcolormesh(fsMesh['x'], fsMesh['y'], Qmesh, vmin = -max, vmax = max, cmap='seismic_r', shading='nearest')
ax.set_xlabel('$\pi_1$')
ax.set_ylabel('$\pi_2$')
cb = fig.colorbar(im, ax=ax, aspect=25, shrink=0.75, pad=0.025)
cb.ax.tick_params(labelsize=9)
if args.Tline:
    tline = pd.read_csv(f'{path}/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
    tline = tline.query('pi2 >= 0.01')
    if args.mask:
        tline['suma'] = tline['pi1'] + tline['pi2']
        tline = tline.query('suma <= 1')
    ax.plot(tline['pi1'], tline['pi2'], color='xkcd:black', lw=0.7)
ax.set_aspect(1.0)
fig.tight_layout(pad=0.1)
fig.savefig(f'stateSpace_asym_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.png')
