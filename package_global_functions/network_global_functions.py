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
    # nodes = [v['name'] for v in g.vs()] # does not work in depaula, igraph==0.10.4
    numNodes = len(g.vs)
    nodes = list(range(g.vs[0].index,g.vs[numNodes-1].index+1))
    # igrpah indexes nodes starting at 0, so:
    if firstID == 1:
        nodes = [n+1 for n in nodes]
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
    
    
def getConfigComSizes(dfconfig, N, firstID = 0):
    """
    input:
        - dfconfigs: df with columns 'contacts0' and 'contacts1'. IDs of the network vertices, 0...N-1 by default; Indicate as argument if they start at 1!!!!!
        - N: number of vertices expected in the network
    output:
        - arrays with the community sizes, community sizes without giant component, and size of the giant component
    """
    if firstID == 1:
        for c in dfconfig.columns:
            dfconfig[c] = dfconfig[c] - 1
    g = ig.Graph.DataFrame(dfconfig, directed=False)
    components = g.components()
    sum_check = 0
    comSizes, comSizes_woGC = [], []
    # com sizes
    for i,com in enumerate(components):
        comSizes.append(len(com))
        sum_check += len(com)
    if(sum_check != N):
        for _ in range(N-sum_check):
            comSizes.append(1)
    # com sizes without the giant component
    index_max = max(range(len(comSizes)), key=comSizes.__getitem__)
    giantComp = comSizes[index_max]
    comSizes_woGC = [c for c in comSizes if c != giantComp]
    if not comSizes_woGC: # i.e. it is an empty list
        comSizes_woGC.append(0)
    return comSizes, comSizes_woGC, giantComp
