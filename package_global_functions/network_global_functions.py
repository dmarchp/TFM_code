import igraph as ig
import numpy as np
import pandas as pd
from .global_functions import *

# def getContactsFromPositions(dfpos):


def getConfigDegrees(dfconfig, N, firstID):
    """
    input:
        - dfconfigs: df with columns 'contacts0' and 'contacts1'. IDs of the network vertices, 0...N-1 or 1...N
        - N: number of vertices expected in the network
        - firstID: lowermost ID, (0 or 1, kilombo or quenched in my workflow)
    output:
        - arrays with the node ID (numeric) and degree (ordered)
        on return nodes are numbered as entered in first ID
    """
    g = ig.Graph.DataFrame(dfconfig, directed=False)
    nodes = [v['name'] for v in g.vs()]
    degrees = []
    for id in range(firstID,N+firstID):
        if id in nodes:
            degrees.append(g.degree(nodes.index(id)))
        else:
            degrees.append(0)
    nodes = [id for id in range(firstID,N+firstID)]
    return nodes, degrees
    
    
def getDegreeDistr(degrees):
    minDeg, maxDeg = min(degrees), max(degrees) # eg 0...3
    binCenters = np.linspace(minDeg, maxDeg, maxDeg - minDeg + 1) # eg 0, 1, 2, 3
    binLims = np.linspace(minDeg, maxDeg+1, (maxDeg+1) - minDeg + 1) # 0, 1, 2, 3, 4 (histogram takes boxes [0,1), [1, 2), ..., [3,4))
    binCenters, prob, dprob = hist1D(degrees, binLims, binCenters, isPDF = True)
    return binCenters, prob, dprob