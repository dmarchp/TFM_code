# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import numpy as np


def histogramBinLog(data, lims, logBoxes):
    if lims[0] < 10 and lims[1] > 10:
        boxLims_leq10 = np.linspace(lims[0],10,11-lims[0])
        boxLims_g10 = np.geomspace(10,lims[1],logBoxes)
        boxLims_g10 = boxLims_g10[1:] # get rid of the 10.0, as it is already in leq10 array
        boxLims = np.concatenate((boxLims_leq10, boxLims_g10), axis=0)
    elif lims[0] > 10:
        boxLims = np.geomspace(lims[0], lims[1], logBoxes)
    elif lims[1] < 10:
        boxLims = np.linspace(lims[0], lims[1], lims[1]-lims[0]+1)
    # compute box centers:
    boxCenters = [(boxSupLim+boxInfLim)/2 for boxSupLim,boxInfLim in zip(boxLims[1:], boxLims[:-1])]
    hist, _ = np.histogram(data, bins=boxLims)
    dens, _ = np.histogram(data, bins=boxLims, density=True)
    return boxCenters, hist, dens
