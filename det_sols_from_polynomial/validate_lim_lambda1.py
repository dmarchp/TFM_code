import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()

parser.add_argument('q1', type=int, help='site 1 quality')
parser.add_argument('q2', type=int, help='site 2 quality')
args = parser.parse_args()

q1, q2 = args.q1, args.q2
r1, r2 = 1/q1, 1/q2
qs, rs = [q1, q2], [r1, r2]

ls = [0.9, 0.99, 0.999]

def fi_l1():
    global r2
    return [r2,0,1-r2]
    
for l in ls:
    det_sol_file = f'res_files/map_asim_q1_{q1}_q2_{q2}_l_{l}.npz'
    data = np.load(det_sol_file)
    fs_lim = fi_l1()
    fsDiff = [[],[],[]]
    for i in range(3):
        fsDiff[i] = data['fs'][i] - fs_lim[i]
    fig, ax = plt.subplots(1,3, figsize=(18,5))
    im0 = ax[0].pcolormesh(data['x'], data['y'], fsDiff[0], cmap='seismic', shading='nearest')
    im1 = ax[1].pcolormesh(data['x'], data['y'], fsDiff[1], cmap='seismic', shading='nearest')
    im2 = ax[2].pcolormesh(data['x'], data['y'], fsDiff[2], cmap='seismic', shading='nearest')
    fig.colorbar(im0, ax=ax[0], aspect=25, shrink=0.75, pad=0.025)
    fig.colorbar(im1, ax=ax[1], aspect=25, shrink=0.75, pad=0.025)
    fig.colorbar(im2, ax=ax[2], aspect=25, shrink=0.75, pad=0.025)
    ax[0].set_xlabel('$\pi_{1,2}$')
    ax[1].set_xlabel('$\pi_{1,2}$')
    ax[2].set_xlabel('$\pi_{1,2}$')
    ax[0].set_ylabel('$\lambda$')
    fig.tight_layout()
    fig.savefig(f'lim_l1_fs_diff_with_teo_l_{l}.png')
