import subprocess
import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import sys
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    path = extSSDpath + getProjectFoldername() + '/det_sols_from_polynomial/res_files'
else:
    print('CAREFUL! NO EXTERNAL SSD!')
    path = '/res_files'


def computeSymetricMap_df(q1, q2, dpi=0.01, pi_lims = (0.01, 0.99),dl=0.01, l_lims = (0.01,0.99)):
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
    pd.to_csv(f'{path}/map_sym_q1_{q1}_q2_{q2}.csv', index=False)

# potser fer un mesh seria mes logic........
def computeSymmetricMap_mesh(q1, q2, dpi=0.01, pi_lims = (0.01, 0.5), dl=0.01, l_lims = (0.00,0.99), npyMesh = True, parqDf = True):
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    Nls = int((l_lims[1] - l_lims[0])/dl) + 1
    xgrid_pi, ygrid_l = np.mgrid[pi_lims[0]:pi_lims[1]:complex(0,Npis), l_lims[0]:l_lims[1]:complex(0,Nls)]
    xgrid_pi, ygrid_l = np.around(xgrid_pi,2), np.around(ygrid_l,2)
    grid_fs = np.empty([3, Npis, Nls])
    for i,pi in tqdm(enumerate(xgrid_pi[:,0])):
        for j,l in enumerate(ygrid_l[0,:]):
            subprocess.call(f'python3 f0poly_sols_clean.py {pi} {pi} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                grid_fs[:,i,j] = sols
                # print(pi, l, sols)
    if npyMesh:
        np.savez(f'{path}/map_sym_q1_{q1}_q2_{q2}.npz', x=xgrid_pi, y=ygrid_l, fs=grid_fs)
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
        df.to_parquet(f'{path}/map_sym_q1_{q1}_q2_{q2}.parquet', index=False)


# ojo no esta del tot aixo...
def computeSymmetricMap_mesh_amp(q1, q2, dpi=0.01, pi_lims = (0.00, 0.5), dl=0.01, l_lims = (0.00,1.00), npyMesh = True, parqDf = True):
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    Nls = int((l_lims[1] - l_lims[0])/dl) + 1
    xgrid_pi, ygrid_l = np.mgrid[pi_lims[0]:pi_lims[1]:complex(0,Npis), l_lims[0]:l_lims[1]:complex(0,Nls)]
    xgrid_pi, ygrid_l = np.around(xgrid_pi,2), np.around(ygrid_l,2)
    grid_fs = np.empty([3, Npis, Nls])
    for i,pi in tqdm(enumerate(xgrid_pi[:,0])):
        for j,l in enumerate(ygrid_l[0,:]):
            subprocess.call(f'python3 f0poly_sols_clean.py {pi} {pi} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                grid_fs[:,i,j] = sols
                # print(pi, l, sols)
    np.savez(f'{path}/map_sym_q1_{q1}_q2_{q2}.npz', x=xgrid_pi, y=ygrid_l, fs=grid_fs)


def computeAsymmetricMap_mesh(q1, q2, l, dpi=0.01, pi_lims = (0.01, 0.99), npyMesh = True, parqDf = True):
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
        np.savez(f'{path}/map_asym_q1_{q1}_q2_{q2}_l_{l}.npz', x=xgrid_pi1, y=ygrid_pi2, fs=grid_fs)
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
        df.to_parquet(f'{path}/map_asym_q1_{q1}_q2_{q2}_l_{l}.parquet', index=False)

def computeAsymmetricMap_df(q1, q2, l, dpi=0.01, pi_lims = (0.01, 0.99)):
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
    df.to_csv(f'{path}/map_asym_q1_{q1}_q2_{q2}_l_{l}.csv', index=False)

def computeAsymmetricMap_mesh_fixPi1(pi1, q1, q2, dpi2=0.01, pi2_lims = (0.01, 0.99), dl=0.01, l_lims = (0.0, 0.99), npyMesh = True, parqDf = True):
    Npi2s = int((pi2_lims[1] - pi2_lims[0])/dpi2) + 1
    Nls = int((l_lims[1]-l_lims[0])/dl) + 1
    xgrid_pi2, ygrid_l = np.mgrid[pi2_lims[0]:pi2_lims[1]:complex(0,Npi2s), l_lims[0]:l_lims[1]:complex(0,Nls)]
    xgrid_pi2, ygrid_l = np.around(xgrid_pi2, 2), np.around(ygrid_l,2)
    grid_fs = np.empty([3, Npi2s, Nls])
    for i,pi2 in enumerate(xgrid_pi2[:,0]):
        for j,l in enumerate(ygrid_l[0,:]):
            print(f'{pi1} {pi2} {q1} {q2} {l}')
            subprocess.call(f'python3 f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
            with open('sols.dat', 'r') as file:
                sols = [float(f) for f in file.readline().split()]
                grid_fs[:,i,j] = sols
    if npyMesh:
        np.savez(f'{path}/map_asym_fixPi1_q1_{q1}_q2_{q2}_pi1_{pi1}.npz', x=xgrid_pi2, y=ygrid_l, fs=grid_fs)
    if parqDf:
        # unpack all grids, fs into lists:
        pi2s = [pi for pi_row in xgrid_pi2 for pi in pi_row]
        ls = [l for l_row in ygrid_l for l in l_row]
        fs = [[],[],[]]
        for i in range(3):
            fs = [fi for fiv in grid_fs[i] for fi in fiv]
        df = pd.DataFrame({'pi2':pi2s, 'l':ls, 'f0':fs[0], 'f1':fs[1], 'f2':fs[2]})
        for k in df.keys():
            df[k] = df[k].astype('float')
        df.to_parquet(f'{path}/map_asym_fixPi1_q1_{q1}_q2_{q2}_pi1_{pi1}.parquet', index=False)


def computeLambdaEvo(pi1, pi2, q1, q2, dl=0.01, l_lims = (0.01, 0.99), noInterac=False):
    Nls = int((l_lims[1] - l_lims[0])/dl) + 1
    ls = np.linspace(l_lims[0], l_lims[1], Nls)
    lambdaEvo = [[],[],[]]
    for l in ls:
        if noInterac:
            subprocess.call(f'python f0poly_sols_clean.py {(1-l)*pi1} {(1-l)*pi2} {q1} {q2} 0.0 > sols.dat', shell=True)
        else:
            subprocess.call(f'python f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
        with open('sols.dat', 'r') as file:
            sols = [float(f) for f in file.readline().split()]
        for i in range(3):
            lambdaEvo[i].append(sols[i])
    df = pd.DataFrame({'lambda':list(ls), 'f0':lambdaEvo[0], 'f1':lambdaEvo[1], 'f2':lambdaEvo[2]})
    # if os.path.exists('res_files/lambdaEvo_results.csv'):
    #     dfglobal = pd.read_csv(f'res_files/lambdaEvo_results.csv')
    #     dfglobal = pd.concat([dfglobal, df], ignore_index=True)
    #     dfglobal = dfglobal.sort_values(by=['pi1', 'pi2', 'q1', 'q2', 'l'], ignore_index=True)
    # else:
    #     dfglobal = df
    # dfglobal.to_csv(f'res_files/lambdaEvo_results.csv')
    if noInterac:
        df.to_csv(f'{path}/lambdaEvo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_noInterac.csv', index=False)
    else:
        df.to_csv(f'{path}/lambdaEvo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}.csv', index=False)

def computeLambdaEvo_v2(pi1, pi2, q1, q2, dl=0.01, l_lims = (0.01, 0.99)):
    Nls = int((l_lims[1] - l_lims[0])/dl) + 1
    ls = np.linspace(l_lims[0], l_lims[1], Nls)
    lambdaEvo = [[],[],[]]
    for l in ls:
        subprocess.call(f'python f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} -v > sols.dat', shell=True)
        sols = []
        with open('sols.dat', 'r') as file:
            for line in file.readlines():
                sols_i = [float(f) for f in line.split()]
                sols.append(sols_i)
        sol_index=0 if l==0.0  else 1 
        for i in range(3):
            lambdaEvo[i].append(sols[sol_index][i])
    df = pd.DataFrame({'l':list(ls), 'f0':lambdaEvo[0], 'f1':lambdaEvo[1], 'f2':lambdaEvo[2]})
    # if os.path.exists('res_files/lambdaEvo_results.csv'):
    #     dfglobal = pd.read_csv(f'res_files/lambdaEvo_results.csv')
    #     dfglobal = pd.concat([dfglobal, df], ignore_index=True)
    #     dfglobal = dfglobal.sort_values(by=['pi1', 'pi2', 'q1', 'q2', 'l'], ignore_index=True)
    # else:
    #     dfglobal = df
    # dfglobal.to_csv(f'res_files/lambdaEvo_results.csv')
    df.to_csv(f'{path}/lambdaEvo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}.csv', index=False)
    # df.to_csv(f'{path}/lambdaEvo_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_around_trans.csv', index=False)

def compute_results_many_params(pi_pairs, q2, q1s, ls):
    df_cols = [[],[],[],[],[],[],[],[]] # pi1, pi2, q1, q2, l, f0, f1, f2
    for pi_pair in pi_pairs:
        pi1, pi2 = pi_pair
        for q1 in q1s:
            for l in ls:
                subprocess.call(f'python f0poly_sols_clean.py {pi1} {pi2} {q1} {q2} {l} > sols.dat', shell=True)
                with open('sols.dat', 'r') as file:
                    sols = [float(f) for f in file.readline().split()]
                df_cols[0].append(pi1)
                df_cols[1].append(pi2)
                df_cols[2].append(q1)
                df_cols[3].append(q2)
                df_cols[4].append(round(l,2))
                df_cols[5].append(sols[0])
                df_cols[6].append(sols[1])
                df_cols[7].append(sols[2])
    df = pd.DataFrame({'pi1':df_cols[0], 'pi2':df_cols[1], 'q1':df_cols[2], 'q2':df_cols[3], 'lamb':df_cols[4], 
                       'f0':df_cols[5], 'f1':df_cols[6], 'f2':df_cols[7]})
    df.to_csv(f'{path}/analytic_res_many_params.csv', index=False)


#for l in [0.9, 0.99, 0.999]:
#    computeAsymmetricMap_mesh(7, 10, l)
#    print(f'done with l={l}')

# computeSymmetricMap_mesh(10, 10, pi_lims=(0.01, 0.5), parqDf=False)
#computeSymmetricMap_mesh(14, 20, pi_lims=(0.01, 0.5), parqDf=False)

# computeAsymmetricMap_mesh(7, 10, 0.8)
# computeAsymmetricMap_mesh(20, 40, 0.6)
# computeAsymmetricMap_mesh(38, 40, 0.9)

# computeAsymmetricMap_mesh_fixPi1(0.25, 10, 10, pi2_lims=(0.01, 0.5), parqDf=False)
# computeAsymmetricMap_mesh_fixPi1(0.25, 7, 10, pi2_lims=(0.01, 0.5), parqDf=False)
# computeAsymmetricMap_mesh_fixPi1(0.25, 9, 10, pi2_lims=(0.01, 0.5), parqDf=False)

# computeLambdaEvo(0.4, 0.2, 5, 10)
# computeLambdaEvo(0.4, 0.2, 10, 20)
# computeLambdaEvo(0.4, 0.2, 15, 30)
# computeLambdaEvo(0.4, 0.2, 20, 40)

# computeLambdaEvo(0.4, 0.2, 7, 10)
# computeLambdaEvo(0.4, 0.2, 14, 20)
# computeLambdaEvo(0.4, 0.2, 21, 30)
# computeLambdaEvo(0.4, 0.2, 28, 40)

# computeLambdaEvo(0.4, 0.2, 9, 10)
# computeLambdaEvo(0.4, 0.2, 18, 20)
# computeLambdaEvo(0.4, 0.2, 27, 30)
# computeLambdaEvo(0.4, 0.2, 36, 40)

# compute_results_many_params([(0.1, 0.1), (0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5), (0.2, 0.1), (0.4, 0.2)],
                            # 10, [1,2,3,4,5,6,7,8,9], np.arange(0.0, 0.9, 0.1))
    
computeLambdaEvo_v2(1e-8, 1e-8, 10.0, 10.0, 0.0001, l_lims=(0.090,0.110))
computeLambdaEvo_v2(1e-6, 1e-6, 10.0, 10.0, 0.0001, l_lims=(0.090,0.110))
computeLambdaEvo_v2(1e-5, 1e-5, 10.0, 10.0, 0.0001, l_lims=(0.090,0.110))
computeLambdaEvo_v2(1e-4, 1e-4, 10.0, 10.0, 0.0001, l_lims=(0.090,0.110))
# computeLambdaEvo_v2(1e-2, 1e-2, 10.0, 10.0, 0.001, l_lims=(0.090,0.150))