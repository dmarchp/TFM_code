import networkx as nwx
import argparse
from datetime import datetime
import sys
from subprocess import call
sys.path.append('../')
from package_global_functions import *

extSSDpath = getExternalSSDpath()
if os.path.exists(extSSDpath):
    ucmPath = extSSDpath + getProjectFoldername() + '/network_models_sim/networks_UCM_gen/'
else:
    ucmPath = 'networks_UCM_gen/'

# how to include UCM
# fortran needs to be modified to accept two different nw_params, the gamma exponent and the minimum degree
# then it needs to be modified to make a call to this program sending two parameters instead of one
# the add argument parser needs to parse through a list...

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('N', type=int, help='Network size')
    parser.add_argument('model', type=str, help='Network model')
    # parser.add_argument('param', type=float, help="Parameter: {'ER':'p', 'BA':'m'}")
    parser.add_argument('params', type=lambda s: [float(item) for item in s.split(',')], help='ER: p, BA: m, UCM: gamma,m,configID')
    args = parser.parse_args()
    N, model, params = args.N, args.model, args.params
    if model == 'BA':
        g = nwx.barabasi_albert_graph(n=N, m=int(params[0]), seed=int(datetime.now().timestamp()))
    elif model == 'ER':
        g = nwx.fast_gnp_random_graph(n=N, p=params[0], seed=int(datetime.now().timestamp()))
    elif model == 'UCM':
        # read configurations stored with these parameters
        gamma, m, configID = params[0], int(params[1]), int(params[2])
        folder = f'N{N}_g{gamma}_min{m}/'
        file = f'N{N}_g{gamma}_min{m}_{configID}.dat'
        g = nwx.read_edgelist(f'{ucmPath}{folder}{file}')
    # I don't know why, but the UCM g does not respect the edgelist order when written, so...
    if model in ['BA', 'ER']:
        nwx.write_edgelist(g, 'nwk.txt', data=False) # revisar que aixo esitgui funcionanyt
    elif model == 'UCM':
        call(f'cp {ucmPath}{folder}{file} nwk.txt', shell=True)
    # write auxiliary degrees file:
    # degrees = [int(round((N-1)*v,3)) for v in nwx.degree_centrality(g).values()]
    degrees = [k for (id,k) in sorted(g.degree(), key=lambda pair: int(pair[0]))]
    kfile = open('nwk_ks.txt', 'w')
    for k in degrees[:-1]:
        kfile.write(f'{k}\n')
    kfile.write(f'{degrees[-1]}')
    kfile.close()

if __name__ == '__main__':
    main()