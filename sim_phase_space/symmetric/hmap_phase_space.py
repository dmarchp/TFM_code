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
parser.add_argument('-mask_ulc', help='Mask upper left corner', action='store_true')
args = parser.parse_args()

q1, q2, N, dataField, ic  = args.q1, args.q2, args.N, args.dataField, args.ic

model = 'Galla'

mesh_file = f'q1_{q1}_q2_{q2}_phase_space_{model}_ic_{ic}_Nbots_{N}.npz'
mesh = np.load(f'{path}/{mesh_file}')

dataField_dic = {
    'f0':{'cmap':'Reds', 'index':0},
    'f1':{'cmap':'Greens', 'index':1},
    'f2':{'cmap':'Blues', 'index':2},
    'sdf0':{'cmap':'magma', 'index':3},
    'sdf1':{'cmap':'magma', 'index':4},
    'sdf2':{'cmap':'magma', 'index':5},
    'Q':{'cmap':'bwr_r', 'index':6},
    'sdQ':{'cmap':'gnuplot', 'index':7}
}

data_mesh = mesh['fs'][dataField_dic[dataField]['index']]

if dataField=='Q':
    maxima = abs(data_mesh).max()
    vmin, vmax = -maxima, maxima
else:
    vmin, vmax = None, None

fig, ax = plt.subplots(figsize=(5.6,4.8))
# im = ax.pcolormesh(mesh['x'], mesh['y'], Qmesh, vmin = -max, vmax = max, cmap='bwr_r', shading='nearest')
im = ax.pcolormesh(mesh['x'], mesh['y'], data_mesh, cmap=dataField_dic[dataField]['cmap'], shading='nearest', vmin=vmin, vmax=vmax) #norm='log'
if args.Tline:
    x = 2
    tline = pd.read_csv(f'{tline_path}/Tline_sym_pis_q1_{float(q1)}_q2_{float(q2)}_f2_{int(x)}f1.csv')
    tline = tline.query('pi >= 0.01')
    ax.plot(tline['pi'], tline['lambda'], color='xkcd:black', lw=0.7)
ax.set_xlabel('$\pi_{1,2}$')
ax.set_ylabel('$\lambda$')
cb = fig.colorbar(im, ax=ax, aspect=25, shrink=0.75, pad=0.025)
cb.ax.tick_params(labelsize=9)
fig.tight_layout(pad=0.1)
# fig.savefig(f'stateSpace_sym_q1_{q1}_q2_{q2}_f2_{int(x)}f1.png')
fig.savefig(f'stateSpaceSimulation_sym_q1_{q1}_q2_{q2}_N_{N}_ic_{ic}_{dataField}.png')
plt.close(fig)