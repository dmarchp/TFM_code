import networkx as nwx
import argparse
from datetime import datetime

# how to include UCM
# fortran needs to be modified to accept two different nw_params, the gamma exponent and the minimum degree
# then it needs to be modified to make a call to this program sending two parameters instead of one
# the add argument parser needs to parse through a list...

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('N', type=int, help='Network size')
    parser.add_argument('model', type=str, help='Network model')
    parser.add_argument('param', type=float, help="Parameter: {'ER':'p', 'BA':'m'}")
    args = parser.parse_args()
    N, model, param = args.N, args.model, args.param
    if model == 'BA':
        g = nwx.barabasi_albert_graph(n=N, m=int(param), seed=int(datetime.now().timestamp()))
    elif model == 'ER':
        g = nwx.fast_gnp_random_graph(n=N, p=param, seed=int(datetime.now().timestamp()))
    elif model == 'UCM':
        # read configurations stored with these parameters
        ...
    nwx.write_edgelist(g, 'nwk.txt', data=False)
    # write auxiliary degrees file:
    # degrees = [int(round((N-1)*v,3)) for v in nwx.degree_centrality(g).values()]
    degrees = [k for (id,k) in sorted(g.degree(), key=lambda pair: pair[0])]
    kfile = open('nwk_ks.txt', 'w')
    for k in degrees[:-1]:
        kfile.write(f'{k}\n')
    kfile.write(f'{degrees[-1]}')
    kfile.close()

if __name__ == '__main__':
    main()