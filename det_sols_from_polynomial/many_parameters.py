import subprocess
import numpy as np
import pandas as pd

# subprocess.call('python f0poly_sols_clean.py 0.1 0.1 7 10 0.5 > sols.dat', shell=True)
# with open('sols.dat', 'r') as file:
#     sols = [float(f) for f in file.readline().split()]

# print(sols)



def computeSimetricMap_df(q1, q2, dpi=0.01, pi_lims = (0.01, 0.99),dl=0.01, l_lims = (0.01,0.99)):
    # future dataframe:
    map = {'pi':[], 'l':[], 'f0':[], 'f1':[], 'f2':[]}
    # loop over phase diagram
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    Nls = int((l_lims[1] - l_lims[0])/dl) + 1
    for i in range(Npis):
        pi = pi_lims[0] + i*dpi
        for j in range(Nls):
            l = l_lims[0] + j*dl
            subprocess.call(f'python f0poly_sols_clean.py {pi} {pi} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
            map['pi'].append(pi), map['l'].append(l)
            map['f0'].append(sols[0]), map['f1'].append(sols[1]), map['f2'].append(sols[2])
    # build and save datagrame
    df = pd.DataFrame(map)
    pd.to_csv(f'res_files/map_sim_q1_{q1}_q2_{q2}.csv', index=False)

# potser fer un mesh seria mes logic........
def computeSimetricMap_mesh(q1, q2, dpi=0.01, pi_lims = (0.01, 0.99), dl=0.01, l_lims = (0.00,0.99), npyMesh = True, parqDf = True):
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    Nls = int((l_lims[1] - l_lims[0])/dl) + dl + 1
    xgrid_pi, ygrid_l = np.mgrid[pi_lims[0]:pi_lims[1]:complex(0,Npis), l_lims[0]:l_lims[1]:complex(0,Nls)]
    xgrid_pi, ygrid_l = np.around(xgrid_pi,2), np.around(ygrid_l,2)
    grid_fs = np.empty([3, Npis, Nls])
    for i,pi in enumerate(xgrid_pi[:,0]):
        for j,l in enumerate(ygrid_l[0,:]):
            subprocess.call(f'python f0poly_sols_clean.py {pi} {pi} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                grid_fs[:,i,j] = sols
    if npyMesh:
        np.savez(f'res_files/map_sim_q1_{q1}_q2_{q2}.npz', x=xgrid_pi, y=ygrid_l, fs=grid_fs)
    if parqDf:
        # unpack all grids, fs into lists:
        pis = [pi for pi_row in xgrid_pi for pi in pi_row]
        ls = [l for l_col in ygrid_l for l in l_col]
        fs = [[],[],[]]
        for i in range(3):
            fs = [fi for fiv in grid_fs[i] for fi in fiv]
        df = pd.DataFrame({'pi':pis, 'l':ls, 'f0':fs[0], 'f1':fs[1], 'f2':fs[2]})
        for k in df.keys():
            df[k] = df[k].astype['float']
        df.to_parquet(f'res_files/map_sim_q1_{q1}_q2_{q2}.parquet', index=False)

def computeASimetricMap_mesh(q1, q2, l, dpi=0.01, pi_lims = (0.01, 0.99), npyMesh = True, parqDf = True):
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    xgrid_pi1, ygrid_pi2 = np.mgrid[pi_lims[0]:pi_lims[1]:complex(0,Npis), pi_lims[0]:pi_lims[1]:complex(0,Npis)]
    xgrid_pi1, ygrid_pi2 = np.around(xgrid_pi1, 2), np.around(ygrid_pi2,2)
    grid_fs = np.empty([3, Npis, Npis])
    for i,pi1 in enumerate(xgrid_pi1[:,0]):
        for j,pi2 in enumerate(ygrid_pi2[0,:]):
            # print(f'{pi1} {pi2} {q1} {q2} {l}')
            subprocess.call(f'python f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                grid_fs[:,i,j] = sols
    if npyMesh:
        np.savez(f'res_files/map_asim_q1_{q1}_q2_{q2}_l_{l}.npz', x=xgrid_pi1, y=ygrid_pi2, fs=grid_fs)
    if parqDf:
        # unpack all grids, fs into lists:
        pi1s = [pi for pi_row in xgrid_pi1 for pi in pi_row]
        pi2s = [pi for pi_row in ygrid_pi2 for pi in pi_row]
        fs = [[],[],[]]
        for i in range(3):
            fs = [fi for fiv in grid_fs[i] for fi in fiv]
        df = pd.DataFrame({'pi1':pi1s, 'pi2':pi2s, 'f0':fs[0], 'f1':fs[1], 'f2':fs[2]})
        for k in df.keys():
            df[k] = df[k].astype('float')
        df.to_parquet(f'res_files/map_asim_q1_{q1}_q2_{q2}_l_{l}.parquet', index=False)



            


def computeAsimetricMap_df(q1, q2, l, dpi=0.01, pi_lims = (0.01, 0.99)):
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    pis = np.linspace(pi_lims[0], pi_lims[1], Npis)
    # future dataframe:
    map = {'pi1':[], 'pi2':[], 'f0':[], 'f1':[], 'f2':[]}
    for pi1 in pis:
        for pi2 in pis:
            subprocess.call(f'python f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
            map['pi1'].append(round(pi1,2)), map['pi2'].append(round(pi2,2))
            map['f0'].append(sols[0]), map['f1'].append(sols[1]), map['f2'].append(sols[2])
    df = pd.DataFrame(map)
    df.to_csv(f'res_files/map_asim_q1_{q1}_q2_{q2}_l_{l}.csv', index=False)



#for l in [0.9, 0.99, 0.999]:
#    computeASimetricMap_mesh(7, 10, l)
#    print(f'done with l={l}')

computeASimetricMap_mesh(7, 10, 0.9999)


