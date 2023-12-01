import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.ndimage import gaussian_filter, gaussian_filter1d
import glob
import sys
import random
from datetime import datetime
from subprocess import call
sys.path.append('../')
from package_global_functions import *
from evo_to_stationary import intEvo, simEvo


def getTimeEvosPath():
    extSSDpath = getExternalSSDpath()
    if os.path.exists(extSSDpath):
        path = extSSDpath + getProjectFoldername() + '/evo_to_stationary/time_evos_dif_cond'
    else:
        path = '/time_evos_dif_cond'
    return path

##########################################################################################################################
####################### Functions to get the stationary time from the integration of the equations #######################
##########################################################################################################################

# compute the time derivatives of fj's from the df of the time evolution
def evoTimeDeriv(dfEvo,Nsites=2):
    dicEvo_dt = {'iter':range(len(dfEvo))}
    for j in range(Nsites+1):
        dfj = []
        for i in range(len(dfEvo)):
            if i == 0: # forward derivative at timestep 0
                dfj.append((dfEvo[f'f{j}'].iloc[1]-dfEvo[f'f{j}'].iloc[0])/(dfEvo['iter'].iloc[1]-dfEvo['iter'].iloc[0]))
            elif i == len(dfEvo)-1: # backwards derivative at the last timestep
                dfj.append((dfEvo[f'f{j}'].iloc[-1]-dfEvo[f'f{j}'].iloc[-2])/(dfEvo['iter'].iloc[-1]-dfEvo['iter'].iloc[-2]))
            else: # central derivative at the last point
                dfj.append(0.5*(dfEvo[f'f{j}'].iloc[i+1]-dfEvo[f'f{j}'].iloc[i-1])/(dfEvo[f'iter'].iloc[i+1]-dfEvo[f'iter'].iloc[i-1]))
        dicEvo_dt[f'df{j}'] = dfj
    dfevo_dt = pd.DataFrame(dicEvo_dt)
    return dfevo_dt

# from the time derivatives get the stationary time:
def getStatTime_evoTimeDeriv(dfEvo, df_dEvodt, thresh=1e-4, Nsites=2):
    # option 1: take the all timesteps
    # stat_times_fjs = [dfEvo['iter'][np.array(abs(df_dEvodt[f'df{j}']) < thresh)].iloc[0] for j in range(Nsites+1)]
    # option 2: discatd the fitst 10 timesteps
    dfEvoAux, df_dEvodtAux = dfEvo.iloc[10:], df_dEvodt.iloc[10:]
    stat_times_fjs = [dfEvoAux['iter'][np.array(abs(df_dEvodtAux[f'df{j}']) < thresh)].iloc[0] for j in range(Nsites+1)]
    # option 3: check that time difference with next stat time is 1 in order to consider it as a valid stationary time
    # stat_times_fjs = []
    # for j in range(Nsites+1):
    #     times_thresh = list(dfEvo['iter'][np.array(abs(df_dEvodt[f'df{j}']) < thresh)])
    #     times_thresh_dif = np.array(times_thresh[1:]) - (times_thresh[:-1])
    #     for i,ttd in enumerate(times_thresh_dif):
    #         if ttd == 1:
    #             stat_times_fjs.append(times_thresh[i])
    stat_time = max(stat_times_fjs)
    Q_at_stat_time = dfEvo['f2'].iloc[stat_time] - 2*dfEvo['f1'].iloc[stat_time]
    return stat_time, Q_at_stat_time


##########################################################################################################################
############################### Functions to get the stationary time from the simulations ################################
##########################################################################################################################

def search_time(w,t,evo,sig=0):
    """
    sig=0 -> no gaussian filter; sig != 0 -> apply gaussian filter with this sigma
    """
    if sig:
        evo_mod = gaussian_filter1d(evo, sig)
    else:
        evo_mod = evo
    time = float('nan')
    for i in range(len(evo_mod)-w):
        block_avg = np.average(evo_mod[i:i+w])
        if abs(evo_mod[i+w+1] - block_avg) < t:
            time = i+w+1
            break
    return time



##########################################################################################################################
#################################### Functions to generate stationary times heatmaps #####################################
##########################################################################################################################

def computeTimesSymmetricMap_mesh(method, q1, q2, dpi=0.01, pi_lims = (0.01, 0.99), dl=0.01, l_lims = (0.00,0.99), 
                                  times_thresh=1e-4,
                                  N=5000, blockSize=50, blockThresh=5e-4, sig=0):
    """
    method: 'int' for numerically integrated evolutim, 'sim' for the time evos
    if method == 'int': times_thresh is used
    if method == 'sim': N (system size), blockSize, blockThresh, sig (gaussian filter sigma) is used
    """
    Npis = int((pi_lims[1] - pi_lims[0])/dpi) + 1
    Nls = int((l_lims[1] - l_lims[0])/dl) + 1
    xgrid_pi, ygrid_l = np.mgrid[pi_lims[0]:pi_lims[1]:complex(0,Npis), l_lims[0]:l_lims[1]:complex(0,Nls)]
    xgrid_pi, ygrid_l = np.around(xgrid_pi,2), np.around(ygrid_l,2)
    grid_time = np.empty([Npis, Nls])
    if method == 'sim':
        grid_counts, grid_time_sd = np.empty([Npis, Nls]), np.empty([Npis, Nls])
    for i,pi in enumerate(xgrid_pi[:,0]):
        for j,l in enumerate(ygrid_l[0,:]):
            if method == 'int':
                file = f'time_evo_csv_pi1_{pi}_pi2_{pi}_q1_{q1}_q2_{q2}_l_{l}_Euler.csv'
                if not os.path.exists(f'{getTimeEvosPath()}/{file}'):
                    intEvo(pi, pi, q1, q2, l, 100, ic='N', bots_per_site=(100, 0, 0), max_time = 1000)
                df = pd.read_csv(f'{getTimeEvosPath()}/{file}')
                df_dt = evoTimeDeriv(df)
                # fetch stationary time, Q for each fj:
                stat_time, Q_at_stat_time = getStatTime_evoTimeDeriv(df, df_dt, times_thresh)
                grid_time[i,j] = stat_time
            elif method == 'sim':
                folder = f'time_evo_csv_N_{N}_pi1_{pi}_pi2_{pi}_q1_{q1}_q2_{q2}_l_{l}'
                if not os.path.exists(f'{getTimeEvosPath()}/{folder}'):
                    # call(f'python evo_to_stationary.py {pi} {pi} {q1} {q2} {l} {N} N {np.random.randint(1,1000000)}', shell=True)
                    simEvo(pi, pi, q1, q2, l, N, ic='N', bots_per_site = [N, 0, 0], max_time = 1000, Nrea=25)
                files = glob.glob(f'{getTimeEvosPath()}/{folder}/*')
                dfs = [pd.read_csv(file) for file in files]
                grid_counts[i,j] = len(dfs)
                times = []
                for df in dfs:
                    time = search_time(w=blockSize, t=blockThresh, evo=df['f2'], sig=sig)
                    times.append(time)
                grid_time[i,j], grid_time_sd = np.average(times), np.std(times)
    if not os.path.exists(f'{getTimeEvosPath()}/stat_times_maps/'):
        call(f'mkdir {getTimeEvosPath()}/stat_times_maps/', shell=True)
    if method == 'int':
        np.savez(f'{getTimeEvosPath()}/stat_times_maps/map_times_sym_q1_{q1}_q2_{q2}.npz', x=xgrid_pi, y=ygrid_l, time=grid_time)
        # np.savez(f'{getTimeEvosPath()}/stat_times_maps/map_times_int_sym_q1_{q1}_q2_{q2}.npz', x=xgrid_pi, y=ygrid_l, time=grid_time)
    elif method == 'sim':
        np.savez(f'{getTimeEvosPath()}/stat_times_maps/map_times_sim_sym_q1_{q1}_q2_{q2}.npz', x=xgrid_pi, y=ygrid_l, 
                 time=grid_time, time_sd=grid_time_sd, counts=grid_counts)


def computeTimesAsymmetricMap_mesh_fixPi1(method, pi1, q1, q2, dpi2=0.01, pi2_lims = (0.01, 0.99), dl=0.01, l_lims = (0.0, 0.99), 
                                          times_thresh=1e-4,
                                          N=5000, blockSize=50, blockThresh=5e-4, sig=0):
    """
    method: 'int' for numerically integrated evolutim, 'sim' for the time evos
    if method == 'int': times_thresh is used
    if method == 'sim': N (system size), blockSize, blockThresh, sig (gaussian filter sigma) is used
    """
    Npi2s = int((pi2_lims[1] - pi2_lims[0])/dpi2) + 1
    Nls = int((l_lims[1]-l_lims[0])/dl) + 1
    xgrid_pi2, ygrid_l = np.mgrid[pi2_lims[0]:pi2_lims[1]:complex(0,Npi2s), l_lims[0]:l_lims[1]:complex(0,Nls)]
    xgrid_pi2, ygrid_l = np.around(xgrid_pi2, 2), np.around(ygrid_l,2)
    grid_time = np.empty([Npi2s, Nls])
    if method == 'sim':
        grid_counts, grid_time_sd = np.empty([Npi2s, Nls]), np.empty([Npi2s, Nls])
    for i,pi2 in enumerate(xgrid_pi2[:,0]):
        for j,l in enumerate(ygrid_l[0,:]):
            if method == 'int':
                file = f'time_evo_csv_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}_Euler.csv'
                if not os.path.exists(f'{getTimeEvosPath()}/{file}'):
                    intEvo(pi1, pi2, q1, q2, l, 100, ic='N', bots_per_site=(100, 0, 0), max_time = 1000)
                df = pd.read_csv(f'{getTimeEvosPath()}/{file}')
                df_dt = evoTimeDeriv(df)
                # fetch stationary time, Q for each fj:
                stat_time, Q_at_stat_time = getStatTime_evoTimeDeriv(df, df_dt, times_thresh)
                grid_time[i,j] = stat_time
            elif method == 'sim':
                folder = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2}_l_{l}'
                if not os.path.exists(f'{getTimeEvosPath()}/{folder}'):
                    # call(f'python evo_to_stationary.py {pi} {pi} {q1} {q2} {l} {N} N {np.random.randint(1,1000000)}', shell=True)
                    simEvo(pi1, pi2, q1, q2, l, N, ic='N', bots_per_site = [N, 0, 0], max_time = 1000, Nrea=25)
                files = glob.glob(f'{getTimeEvosPath()}/{folder}/*')
                dfs = [pd.read_csv(file) for file in files]
                grid_counts[i,j] = len(dfs)
                times = []
                for df in dfs:
                    time = search_time(w=blockSize, t=blockThresh, evo=df['f2'], sig=sig)
                    times.append(time)
                grid_time[i,j], grid_time_sd = np.average(times), np.std(times)
    if not os.path.exists(f'{getTimeEvosPath()}/stat_times_maps/'):
        call(f'mkdir {getTimeEvosPath()}/stat_times_maps/', shell=True)
    if method == 'int':
        np.savez(f'{getTimeEvosPath()}/stat_times_maps/map_times_asym_fixPi1_q1_{q1}_q2_{q2}_pi1_{pi1}.npz', x=xgrid_pi2, y=ygrid_l, time=grid_time)
        # np.savez(f'{getTimeEvosPath()}/stat_times_maps/map_times_int_asym_fixPi1_q1_{q1}_q2_{q2}_pi1_{pi1}.npz', x=xgrid_pi2, y=ygrid_l, time=grid_time)
    elif method == 'sim':
        np.savez(f'{getTimeEvosPath()}/stat_times_maps/map_times_sim_asym_fixPi1_q1_{q1}_q2_{q2}_pi1_{pi1}.npz', x=xgrid_pi2, y=ygrid_l, 
                 time=grid_time, time_sd=grid_time_sd, counts=grid_counts)



if __name__ == '__main__':
    # computeTimesSymmetricMap_mesh('sim', 7, 10, dpi=0.025, pi_lims=(0.05, 0.5), dl=0.05, l_lims=(0.0, 0.95))
    # computeTimesAsymmetricMap_mesh_fixPi1('sim', 0.25, 7, 10, dpi2=0.025, pi2_lims=(0.05, 0.5), dl=0.05, l_lims=(0.0, 0.95))
    # Maximal precision:
    computeTimesSymmetricMap_mesh('sim', 7, 10)
    print('Finished the symmetric map')
    computeTimesAsymmetricMap_mesh_fixPi1('sim', 0.25, 7, 10)