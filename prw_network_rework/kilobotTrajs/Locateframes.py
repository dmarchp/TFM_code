import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience

import pims
import trackpy as tp

# change the following to %matplotlib notebook for interactive plotting
#%matplotlib inline

# Optionally, tweak styles.
mpl.rc('figure',  figsize=(10, 5))
mpl.rc('image', cmap='gray')



@pims.pipeline
def gray(image): 
    #Final_image: red_image[:,:,1]+ green_image[:,:,1]+blue_image[:,:,2])
    Final_image= image[:,:,0]+image[:,:,1]+image[:,:,2]
    return Final_image# Take the  green channel

frames = gray(pims.open(r"Images/*.png"))

f=[]

for i in range(1, len(frames)):
    f.append(tp.locate(frames[i], 39, invert=False, minmass=1000))

# Save data into a CSV file
data = pd.concat(f)
data.to_csv('located_frames_data.csv', index=False)
