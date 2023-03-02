import igraph as ig
import numpy as np
import pandas as pd

# def getContactsFromPositions(dfpos):


def getConfigDegrees(dfconfig, N):
    """
    input:
        - dfconfigs: df with columns 'contacts0' and 'contacts1'. IDs of the network vertices, 0...N-1 or 1...N
        - N: number of vertices expected in the network
    output:
        - arrays with the node ID (numeric) and degree (ordered)
        on return nodes are numbered 1...N
    """
    g = ig.Graph.DataFrame(dfconfig, directed=False)
    nodes = [v['name'] for v in g.vs()]
    degrees = []
    for i in range(1,N+1):
        if i in nodes:
            degrees.append(g.degree(nodes.index(i)))
        else:
            degrees.append(0)
    nodes = [i for i in range(1,N+1)]
    return nodes, degrees