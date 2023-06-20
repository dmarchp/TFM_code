import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
import argparse
import socket
import sys
sys.path.append('../../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/sim_phase_space/symmetric/results'
    tline_path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    print('CAREFUL! NO EXTERNAL SSD!')
    path = './results'
    tline_path = '../../det_sols_from_polynomial/res_files'

parser = argparse.ArgumentParser()
parser.add_argument('q1', type=float, help='site 1 quality')
parser.add_argument('q2', type=float, help='site 2 quality')
parser.add_argument('N', type=int, help='Number of bots to simulate')
parser.add_argument('dataField', type=str, help='Which data to heatmap: f0,f1,f2,sdf0,sdf1,sdf2,Q,sdQ')
parser.add_argument('--ic', type=str, help='Initial condition: (no (all uncomitted), pi, pi hard) -> (N/P/Phard)', default='N')
parser.add_argument('-Tline', help='Add theoretical transition line to the colormap plot', action='store_true')
parser.add_argument('--mask_ulc', type=int, help='Mask upper left corner', default=0)
args = parser.parse_args()

q1, q2, N, dataField, ic  = args.q1, args.q2, args.N, args.dataField, args.ic

model = 'Galla'

mesh_file = f'q1_{q1}_q2_{q2}_phase_space_{model}_ic_{ic}_Nbots_{N}.npz'
mesh = np.load(f'{path}/{mesh_file}')

dataField_dic = {
    'f0':{'cmap':'Reds', 'index':0, 'tline_color':'xkcd:black'},
    'f1':{'cmap':'Greens', 'index':1, 'tline_color':'xkcd:black'},
    'f2':{'cmap':'Blues', 'index':2, 'tline_color':'xkcd:green'},
    'sdf0':{'cmap':'magma', 'index':3, 'tline_color':'xkcd:green'},
    'sdf1':{'cmap':'magma', 'index':4, 'tline_color':'xkcd:green'},
    'sdf2':{'cmap':'magma', 'index':5, 'tline_color':'xkcd:black'},
    'Q':{'cmap':'bwr_r', 'index':6, 'tline_color':'xkcd:black'},
    'sdQ':{'cmap':'gnuplot', 'index':7, 'tline_color':'xkcd:green'}
}

data_mesh = mesh['fs'][dataField_dic[dataField]['index']]

if dataField=='Q':
    maxima = abs(data_mesh).max()
    vmin, vmax = -maxima, maxima
else:
    vmin, vmax = None, None

if args.mask_ulc == 1:
    data_mesh[0][-1] = float('nan')
elif args.mask_ulc == 2:
    data_mesh[0][-2:] = float('nan')
    data_mesh[1][-1] = float('nan')
elif args.mask_ulc == 3:
    data_mesh[0][-3:] = float('nan')
    data_mesh[1][-2:] = float('nan')
    data_mesh[2][-1] = float('nan')


fig, ax = plt.subplots(figsize=(5.6,4.8))
# im = ax.pcolormesh(mesh['x'], mesh['y'], Qmesh, vmin = -max, vmax = max, cmap='bwr_r', shading='nearest')
im = ax.pcolormesh(mesh['x'], mesh['y'], data_mesh, cmap=dataField_dic[dataField]['cmap'], shading='nearest', vmin=vmin, vmax=vmax) #norm='log'
if args.Tline:
    x = 2
    tline = pd.read_csv(f'{tline_path}/Tline_sym_pis_q1_{float(q1)}_q2_{float(q2)}_f2_{int(x)}f1.csv')
    tline = tline.query('pi >= 0.01')
    ax.plot(tline['pi'], tline['lambda'], color=dataField_dic[dataField]['tline_color'], lw=0.7)
ax.set_xlabel('$\pi_{1,2}$')
ax.set_ylabel('$\lambda$')
cb = fig.colorbar(im, ax=ax, aspect=25, shrink=0.75, pad=0.025)
cb.ax.tick_params(labelsize=9)
fig.tight_layout(pad=0.1)
fig.text(0.87, 0.95, rf'$q_1 = {q1}$', fontsize=8)
fig.text(0.87, 0.92, rf'$q_2 = {q2}$', fontsize=8)
fig.text(0.87, 0.89, rf'$N = {N}$', fontsize=8)
fig.savefig(f'stateSpaceSimulation_sym_q1_{q1}_q2_{q2}_N_{N}_ic_{ic}_{dataField}.png')
plt.close(fig)