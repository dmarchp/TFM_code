import matplotlib.pyplot as plt
import numpy as np

def plotSymmetricMap_mesh(q1, q2):
    x = 2
    fsMesh = np.load(f'map_sym_q1_{q1}_q2_{q2}_lattice.npz')
    # Qmesh = fsMesh['fs'][2] - x*fsMesh['fs'][1]
    fig, ax = plt.subplots(1,3,figsize=(12, 4), constrained_layout=True)
    for i in range(3):
        ax[i].set_xlim(-0.005, 0.505)
        ax[i].set_ylim(-0.005, 1.005)
        ax[i].set_xlabel('$\pi_{1,2}$')
    ax[0].set_ylabel('$\lambda$')

    contour_levels = {'f0':[0.1, 0.2, 0.4, 0.6, 0.8],
                  'f1':[0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                  'f2':[0.1, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.8999999]}

    fs_cmaps = {'f0':'Reds', 'f1':'Greens', 'f2':'Blues'}
    fs_labels_xpos = {'f0':0.06, 'f1':0.387, 'f2':0.715}
    fs_labels_cbar = {'f0':r'\textbf{$f_0$}', 'f1':r'$f_1$', 'f2':r'$f_2$'}
    fs_labels_fig = {'f0':r'$\textbf{A}$', 'f1':r'$\textbf{B}$', 'f2':r'$\textbf{C}$'}

    for i,f in enumerate(['f0', 'f1', 'f2']):
        im = ax[i].pcolormesh(fsMesh['x'], fsMesh['y'], fsMesh['fs'][i], vmin =0, vmax =1, cmap=fs_cmaps[f], shading='nearest', rasterized=True)
        con = ax[i].contour(fsMesh['x'], fsMesh['y'], fsMesh['fs'][i], levels=contour_levels[f], linewidths=0.8)
        fig.colorbar(im, ax=ax[i], location='top', fraction=0.05, aspect=35, pad=0.02, shrink=0.83, anchor=(0.96, 1.0))
        ax[i].clabel(con)
    fig.text(fs_labels_xpos[f], 0.92, fs_labels_cbar[f])
    fig.text(fs_labels_xpos[f], 0.82, fs_labels_fig[f])
    fig.savefig(f'fs_cmaps_lattice_isolines_sym_pi_q1_{q1}_q2_{q2}.pdf')