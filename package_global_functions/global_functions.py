# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import numpy as np
import matplotlib.pyplot as plt

def histogramBinLog(data, lims, logBoxes):
    if lims[0] < 10 and lims[1] > 10:
        boxLims_leq10 = np.linspace(lims[0],10,11-lims[0])
        boxLims_g10 = np.geomspace(10,lims[1],logBoxes)
        boxLims_g10 = boxLims_g10[1:] # get rid of the 10.0, as it is already in leq10 array
        boxLims = np.concatenate((boxLims_leq10, boxLims_g10), axis=0)
    elif lims[0] > 10:
        boxLims = np.geomspace(lims[0], lims[1], logBoxes)
        boxCenters = []
    elif lims[1] < 10:
        boxLims = np.linspace(lims[0], lims[1], lims[1]-lims[0]+1)
    # compute box centers:
    boxCenters = [(boxSupLim+boxInfLim)/2 for boxSupLim,boxInfLim in zip(boxLims[1:], boxLims[:-1])]
    hist, _ = np.histogram(data, bins=boxLims)
    dens, _ = np.histogram(data, bins=boxLims, density=True)
    return boxCenters, hist, dens    

### ATENCIO: PEL BIN CENTER DE LA PART LOGARITMICA HAURE DE FER CENTER = NP.SQRT(INF*SUP)
def binsForHist1D_log(lims: tuple[float], logBoxes: int):
    """
    creates a sequence with the box limits for an Histogram. 
    From 1 to 10 the boxes will be spaced linearly (spacing 1); 
    from 10 up, they will be spaced logarithmically (with N=logBoxes boxes)
    -------
    Returns
    -------
    boxLims: inferior limit of boxes + last sup limit
    boxCenters
    """
    if lims[0] < 10 and lims[1] > 10:
        boxLims_leq10 = np.linspace(lims[0],10,11-lims[0])
        boxLims_g10 = np.geomspace(10,lims[1],logBoxes)
        boxLims_g10 = boxLims_g10[1:] # get rid of the 10.0, as it is already in leq10 array
        boxLims = np.concatenate((boxLims_leq10, boxLims_g10), axis=0)
        # boxCenters_leq10 = (boxLims_leq10[1:]+boxLims_leq10[:-1])/2
        boxCenters = np.sqrt(boxLims[1:]*boxLims[:-1])
    elif lims[0] > 10:
        boxLims = np.geomspace(lims[0], lims[1], logBoxes)
        boxCenters = np.sqrt(boxLims[1:]*boxLims[:-1])
    elif lims[1] < 10:
        boxLims = np.linspace(lims[0], lims[1], lims[1]-lims[0]+1)
        boxCenters = (boxLims[1:]+boxLims[:-1])/2
    return boxLims, boxCenters


def hist1D(x, Bins, binCenter, isPDF, isNonZero = True):
    """
    Calculates the 1D histogram of an x variable using bin edges (Bins) and returns the histogram H, its error dH and the bin centers (binCenter) only for nonzero bins.
    Parameters
    ----------
    Returns
    -------
    binCenter, H, dH
    """    
    if isPDF == False:
        H = np.histogram(x, bins = Bins)[0]
        dH = np.sqrt( H*(1-H/(len(x)) ))
    else:
        dBins = Bins[1:] - Bins[:-1]
        H = np.histogram(x, bins = Bins, density=True)[0]
        dH = np.sqrt( H*(1-H*dBins)/(len(x)*dBins) )
    if isNonZero:
        nonZ = H!=0
        binCenter = binCenter[nonZ]
        H = H[nonZ]
        dH = dH[nonZ]
    return binCenter, H, dH
    
def latexFont(size= 15, labelsize=18, titlesize=20, ticklabelssize=15, legendsize = 18):
    plt.rcParams.update({
        "text.usetex": True})
    plt.rcParams["text.latex.preamble"].join([
        r"\usepackage{underscore}", r"\usepackage{color}"
    ])
    plt.rcParams["font.family"] = 'STIXGeneral'
    plt.rc('font', size=size)          # controls default text sizes
    plt.rc('axes', titlesize=titlesize)     # fontsize of the axes title
    plt.rc('axes', labelsize=labelsize)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=ticklabelssize)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=ticklabelssize)    # fontsize of the tick labels
    plt.rc('legend', fontsize=legendsize)    # legend fontsize
    plt.rc('figure', titlesize=titlesize)  # fontsize of the figure title
    
    
