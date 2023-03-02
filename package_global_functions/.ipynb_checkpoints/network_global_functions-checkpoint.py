import igraph as ig
import numpy as np
import pandas as pd



def getConfigDegrees(dfconfig, N):
    """
    input:
        - dfconfigs: df with columns 'contacts0' and 'contacts1'. IDs of the network vertices, 0...N-1 or 1...N
        - N: number of vertices expected in the network
    output:
        - arrays with the node ID and degree (ordered)
    """
    g = ig.Graph.DataFrame(dfconfig, directed=False)
    nodes = [v['name'] for v in g.vs()]
    degrees = []
    for i in range(1,N+1):
        if i in nodes:
            print(i)
            degrees.append(g.degree(nodes.index(i)))
        else:
            degrees.append(0)