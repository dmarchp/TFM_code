#%%
import numpy as np
import pandas as pd

# https://stackoverflow.com/questions/40554179/how-to-keep-column-names-when-converting-from-pandas-to-numpy

filenameConfig = 'raw_json_files/RWDIS_mod/configs/PRW_nBots_35_ar_20.0_speed_7_speedVar_2_001.csv'
filenameConfignp = 'raw_json_files/RWDIS_mod/configs/PRW_nBots_35_ar_20.0_speed_7_speedVar_2_001.npy'
dfconfigs = pd.read_csv(filenameConfig)
# configs = dfconfigs.to_numpy()
# print(configs)
# np.save(filenameConfignp, configs)

#%%
arr_ip = [tuple(i) for i in dfconfigs.to_numpy()]
dtyp = np.dtype(list(zip(dfconfigs.dtypes.index, dfconfigs.dtypes)))
arr = np.array(arr_ip, dtype=dtyp)
print(dtyp)
print(arr)
np.save(filenameConfignp, arr)

# amb això puc accedir a les columnes fent
# arr['x_position'], arr['y_position'], arr['xticks']
# %%
