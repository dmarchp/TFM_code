"""
This program is intended to process the kilombo spatial configuration files or contact files
, i.e. to extract data such as 
degrees, community sizes (w/wo giant component) and store it in a file for later use
"""
import pandas as pd
import glob
import os
import sys
sys.path.append('../')
from package_global_functions import *
from filesHandling_kilombo import getFilenameRoot, getFilenameINTContactSufix, getConfigsPath

def getDegreesAllTraj(N, arena_r, interac_r, loops):
    fname = getFilenameRoot(N, arena_r)
    fnameSufix = getFilenameINTContactSufix(loops, interac_r)
    contactsPath = getConfigsPath() + '/contacts'
    existingFiles = len(glob.glob(contactsPath + '/' + fname + '_*' + fnameSufix))
    print(existingFiles)

if __name__ == '__main__':
    getDegreesAllTraj(35, 18.5, 7.0, 800)