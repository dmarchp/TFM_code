import subprocess
import numpy as np


def computeSymmetricMap_mesh_amp(q1, q2, dpi=0.01, pi_lims = (0.00, 0.5), dl=0.01, l_lims = (0.00,1.00), npyMesh = True, parqDf = True):
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    Nls = int((l_lims[1] - l_lims[0])/dl) + 1
    xgrid_pi, ygrid_l = np.mgrid[pi_lims[0]:pi_lims[1]:complex(0,Npis), l_lims[0]:l_lims[1]:complex(0,Nls)]
    xgrid_pi, ygrid_l = np.around(xgrid_pi,2), np.around(ygrid_l,2)
    grid_fs = np.empty([3, Npis, Nls])
    for i,pi in enumerate(xgrid_pi[:,0]):
        for j,l in enumerate(ygrid_l[0,:]):
            # por ejemplo aqui calculo las soluciones del polinomio, las guardo en un fichero y las leo
            # para despues guardar los valores en el array de dimension (3, Npis, Nls)
            subprocess.call(f'python3 f0poly_sols_clean.py {pi} {pi} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                grid_fs[:,i,j] = sols
                # print(pi, l, sols)
    np.savez(f'map_sym_q1_{q1}_q2_{q2}_lattice.npz', x=xgrid_pi, y=ygrid_l, fs=grid_fs)