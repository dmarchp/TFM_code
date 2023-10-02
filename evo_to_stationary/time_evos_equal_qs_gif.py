import pandas as pd
import matplotlib.pyplot as plt
import glob
from functools import reduce
from subprocess import call
import random
import imageio.v2 as imageio
from datetime import datetime
import sys
sys.path.append('../')
from package_global_functions import *

N = 100000
pi1, pi2, q = 0.1, 0.1, 10
lambdas = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.99, 0.999, 0.9999]
random.seed(datetime.now().timestamp())

gifName = f'time_evos_multiplot_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q}_q2_{q}_many_lambdas.gif'

# same function as in plot_evos.py
def getTimeEvosPath():
    extSSDpath = getExternalSSDpath()
    if os.path.exists(extSSDpath):
        path = extSSDpath + getProjectFoldername() + '/evo_to_stationary/time_evos_dif_cond'
    else:
        path = '/time_evos_dif_cond'
    return path

def get_avg_traj(dfs):
    df_avg = reduce(lambda a,b: a.add(b, fill_value=0), dfs)
    df_avg = df_avg/len(dfs)
    return df_avg


for j,l in enumerate(lambdas):
    folder = f'time_evo_csv_N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q}_q2_{q}_l_{l}'
    if not os.path.exists(f'{getTimeEvosPath()}/{folder}/'):
        call(f'python evo_to_stationary.py {pi1} {pi2} {q} {q} {l} {N} N {random.randint(0,1000000)}', shell=True)
    files = glob.glob(f'{getTimeEvosPath()}/{folder}/*')
    dfs = [pd.read_csv(file) for file in files]
    df_avg = get_avg_traj(dfs)
    Nplots = 6
    fig, ax = plt.subplots(2, int(Nplots/2), figsize=(10.8, 4.8), constrained_layout=True)
    ax[0,0].set_ylabel(r'$f_j$')
    ax[1,0].set_ylabel(r'$f_j$')
    ax[1,0].set_xlabel(r'time')
    ax[1,1].set_xlabel(r'time')
    ax[1,2].set_xlabel(r'time')
    for i,df in enumerate(dfs[:Nplots]):
        ax[int(i//(Nplots/2)),int(i%(Nplots/2))].plot(df['iter'], df['f0'], alpha=0.8, lw=0.6, color='xkcd:red')
        ax[int(i//(Nplots/2)),int(i%(Nplots/2))].plot(df['iter'], df['f1'], alpha=0.8, lw=0.6, color='xkcd:green')
        ax[int(i//(Nplots/2)),int(i%(Nplots/2))].plot(df['iter'], df['f2'], alpha=0.8, lw=0.6, color='xkcd:blue')
        ax[int(i//(Nplots/2)),int(i%(Nplots/2))].set_xscale('symlog')
    fig.text(0.07, 0.8, f'$\lambda = {l}$', fontsize=12)
    fig.text(0.07, 0.75, f'$N = {N}$', fontsize=12)
    fig.savefig(f'figure_for_gif_{str(j).zfill(3)}.png')

figures = sorted(glob.glob('figure_for_gif_*.png'))
with imageio.get_writer(f'{gifName}', mode='I', duration=1000.0) as writer: # duration en ms ??????
    for figure in figures:
        image = imageio.imread(figure)
        writer.append_data(image)

call('mkdir -p time_evos_multiplots', shell=True)
call(f'mkdir -p time_evos_multiplots/N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q}_q2_{q}', shell=True)
call(f'mv figure_for_gif_*.png time_evos_multiplots/N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q}_q2_{q}/', shell=True)
call(f'mv {gifName} time_evos_multiplots/N_{N}_pi1_{pi1}_pi2_{pi2}_q1_{q}_q2_{q}/', shell=True)