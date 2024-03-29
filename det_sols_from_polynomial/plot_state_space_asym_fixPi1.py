# plot the phase space + Tline for a specific pi1, x=pi2, y=lambda
import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    print('CAREFUL! NO EXTERNAL SSD!')
    path = '/res_files'

parser = argparse.ArgumentParser()
parser.add_argument('q1', type=int, help='site 1 quality')
parser.add_argument('q2', type=int, help='site 2 quality')
parser.add_argument('pi1', type=float, help='site 1 discovery probability (pi1)')
parser.add_argument(
    'x', type=float, help='factor between f1 and f2, f2 = x*f1')
parser.add_argument('-Tline', help='Add theoretical transition line to the colormap plot', action='store_true')
parser.add_argument('-Tline_both', help='Add theoretical both consensus defs transition lines to the colormap plot', action='store_true')
parser.add_argument('-f2', help='Plot also the map for f2', action='store_true')

args = parser.parse_args()

q1, q2, pi1, x = args.q1, args.q2, args.pi1, args.x

fsMesh = np.load(f'{path}/map_asym_fixPi1_q1_{q1}_q2_{q2}_pi1_{pi1}.npz')
Qmesh = fsMesh['fs'][2] - x*fsMesh['fs'][1]
sumXY = fsMesh['x'] + fsMesh['y']

max = abs(Qmesh).max()
max = 1.0

fig, ax = plt.subplots(figsize=(5.6,4.8))
im = ax.pcolormesh(fsMesh['x'], fsMesh['y'], Qmesh, vmin = -max, vmax = max, cmap='seismic_r', shading='nearest')
ax.set_xlabel('$\pi_2$')
ax.set_ylabel('$\lambda$')
ax.set_ylim(0,None)
cb = fig.colorbar(im, ax=ax, aspect=25, shrink=0.7, pad=0.025)
cb.ax.tick_params(labelsize=9)
# Tlines:
if args.Tline_both:
    xvect, lstyles = [1, 2], ['-.', '-']
elif args.Tline:
    xvect, lstyles = [x,], ['-']
else:
    xvect, lstyles = [], []
for x,ls in zip(xvect,lstyles):
    tline = pd.read_csv(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{float(q1)}_q2_{float(q2)}_f2_{int(x)}f1.csv')
    tline = tline.query('pi2 >= 0.005')
    tline = tline.rename(columns={'lambda':'l'})
    i_last_pi2 = tline.query('l != l').iloc[0].name
    tline.at[i_last_pi2, 'l'] = 0.0
    ax.plot(tline['pi2'], tline['l'], color='xkcd:black', lw=0.7, ls=ls)
# vertical line to show the value of pi1:
ax.axvline(pi1, ls=':', color='xkcd:black', lw=0.7)
# ax.set_aspect(1.0)
fig.text(0.9, 0.96, f'$\pi_1 = {pi1}$', fontsize=8)
fig.text(0.9, 0.92, f'$q_1 = {q1}$', fontsize=8)
fig.text(0.9, 0.88, f'$q_2 = {q2}$', fontsize=8)
fig.tight_layout(pad=0.1)
fig.savefig(f'stateSpace_asym_fixPi1_q1_{q1}_q2_{q2}_pi1_{pi1}_f2_{int(x)}f1.png')
plt.close(fig)

if args.f2:
    fig, ax = plt.subplots(figsize=(5.6,4.8))
    im = ax.pcolormesh(fsMesh['x'], fsMesh['y'], fsMesh['fs'][2], vmin = 0, vmax = 1, cmap='PuOr', shading='nearest')
    ax.set_xlabel('$\pi_2$')
    ax.set_ylabel('$\lambda$')
    ax.set_ylim(0,None)
    cb = fig.colorbar(im, ax=ax, aspect=25, shrink=0.7, pad=0.025)
    cb.ax.tick_params(labelsize=9)
    # Tlines:
    if args.Tline_both:
        xvect, lstyles = [1, 2], ['-.', '-']
    elif args.Tline:
        xvect, lstyles = [x,], ['-']
    else:
        xvect, lstyles = [], []
    for x,ls in zip(xvect,lstyles):
        tline = pd.read_csv(f'{path}/Tline_asym_fixPi1_pi1_{pi1}_q1_{float(q1)}_q2_{float(q2)}_f2_{int(x)}f1.csv')
        tline = tline.query('pi2 >= 0.005')
        tline = tline.rename(columns={'lambda':'l'})
        i_last_pi2 = tline.query('l != l').iloc[0].name
        tline.at[i_last_pi2, 'l'] = 0.0
        ax.plot(tline['pi2'], tline['l'], color='xkcd:black', lw=0.7, ls=ls)
    # vertical line to show the value of pi1:
    ax.axvline(pi1, ls=':', color='xkcd:black', lw=0.7)
    # ax.set_aspect(1.0)
    fig.text(0.9, 0.96, f'$\pi_1 = {pi1}$', fontsize=8)
    fig.text(0.9, 0.92, f'$q_1 = {q1}$', fontsize=8)
    fig.text(0.9, 0.88, f'$q_2 = {q2}$', fontsize=8)
    fig.tight_layout(pad=0.1)
    fig.savefig(f'stateSpace_asym_fixPi1_q1_{q1}_q2_{q2}_pi1_{pi1}_f2.png')
    plt.close(fig)