#%%
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
# from package_global_functions import *
from filesHandling_kilombo import *

# everything in milimeters
arena_r = 185.0
exclusion_r = 15.0
interac_r = 55.0
cicle = 10
loops = 800

N = 25
jumpTrajConfigs = 5


# parquet files:
filenameConfig = getConfigsPath() + '/' + getFilenameRoot(N, arena_r/10) + getFilenameNumber(1) + getFilesExtension()
filenameContact = getConfigsPath() + '/contacts/' + getFilenameRoot(N, arena_r/10) + getFilenameNumber(1) + getFilenameContactSufix(loops, interac_r/10)
dfconfigs = pd.read_parquet(filenameConfig)
dfcontacts = pd.read_parquet(filenameContact)

ids = pd.unique(dfconfigs['ID'])
Nbots = len(ids)
dfcicle0 = dfcontacts.loc[dfcontacts['cicleID']==cicle]
configs0 = pd.unique(dfcicle0['configID'])
print(configs0)
# input('enter ')

# per interac_r 34
# configs0 = np.linspace(24,39,16)
# configs0 = [int(c) for c in configs0]

def dist2D(pos0, pos1):
    return np.sqrt((pos0[0]-pos1[0])**2+(pos0[1]-pos1[1])**2)

def getDistances(positions, i, cicle, interac_r):
    dists = []
    for k,pos0 in enumerate(positions[:-1]):
        for pos1 in positions[k+1:]:
            dists.append(dist2D(pos0, pos1))
    dists = np.array(dists)
    dists = dists[dists < 40.0]
    figD, axD = plt.subplots()
    axD.hist(dists)
    axD.axvline(interac_r, ls='--', color='k')
    figD.tight_layout()
    figD.savefig(f'histoDists_config_{str(i).zfill(3)}_cicle_{cicle}.png')
    dists = dists[dists <= interac_r]
    print(f'{len(dists)} distances smaller thant interac_r')

#%%
for i in configs0:
    df_single_config_contacts = dfcicle0.loc[dfcicle0['configID']==i].copy(deep=True)
    df_single_config_contacts.drop(labels=['cicleID', 'configID'], axis='columns', inplace=True)
    g = ig.Graph.DataFrame(df_single_config_contacts, directed=False)
    if g.vcount() < Nbots:
        vertices_ids = [v['name'] for v in g.vs]
        lacking_vertices = [v for v in range(Nbots) if v not in vertices_ids]
        for v in lacking_vertices:
            g.add_vertex(name=v)
    imod = i*jumpTrajConfigs
    df_single_config = dfconfigs.loc[(imod*Nbots):(imod*Nbots+Nbots-1)]
    true_layout = []
    vertices_ids = [v['name'] for v in g.vs]
    for j in vertices_ids:
        x, y = float(df_single_config.loc[df_single_config['ID']==j]['x_position']), float(df_single_config.loc[df_single_config['ID']==j]['y_position'])
        true_layout.append([x,y])
    # getDistances(true_layout, i, cicle, interac_r)
    true_layout = ig.Layout(true_layout)
    fig, ax = plt.subplots(figsize=(5,5))
    ig.plot(
        g, target=ax, layout=true_layout, vertex_size = 2, vertex_color = 'steelblue', vertex_frame_width = 1.0, 
        vertex_frame_color = 'white'
    )
    circle = plt.Circle([0.0, 0.0], arena_r+exclusion_r, fill=False, edgecolor = 'k')
    ax.add_patch(circle)
    ax.set_xlim(-(arena_r+exclusion_r+1), arena_r+exclusion_r+1)
    ax.set_ylim(-(arena_r+exclusion_r+1), arena_r+exclusion_r+1)
    fig.suptitle(f'config {i} in cycle {cicle}')
    for j,v in enumerate(vertices_ids):
        coords = true_layout[j]
        circle = plt.Circle(tuple(coords), exclusion_r, color='xkcd:purple', alpha=0.5, clip_on = False)
        ax.add_patch(circle)
        # ax.text(coords[0], coords[1], f'{v}')
    # extra: show interaction radius for the ID 0 bot
    id0pos = (float(df_single_config.query('ID == 0')['x_position']), float(df_single_config.query('ID == 0')['y_position']))
    circle = plt.Circle(id0pos, interac_r, fill=False, edgecolor='xkcd:grey', ls='--')
    ax.add_patch(circle)
    fig.savefig(f'config_{str(i).zfill(3)}_cicle_{cicle}.png')
    plt.close(fig)

#%%
# print the corresponding integrated config:
filenameContactInt = getConfigsPath() + '/contacts/' + getFilenameRoot(N, arena_r/10) + getFilenameNumber(1) + getFilenameContactIntSufix(loops, interac_r/10)
dfcontactsINT = pd.read_parquet(filenameContactInt)
dfcontactsINTcicle0 = dfcontactsINT.loc[dfcontactsINT['cicleID']==cicle].copy(deep=True)
dfcontactsINTcicle0.drop(labels='cicleID', axis='columns', inplace=True)
# dfcontactsINTcicle0.sort_values(by=['contacts0', 'contacts1'], inplace=True)
# dfcontactsINTcicle0.reset_index(drop=True, inplace=True)
g = ig.Graph.DataFrame(dfcontactsINTcicle0, directed=False)
print(g.vcount())
if g.vcount() < Nbots:
    print('here')
    vertices_ids = [v['name'] for v in g.vs]
    lacking_vertices = [v for v in range(Nbots) if v not in vertices_ids]
    #print(lacking_vertices)
    for v in lacking_vertices:
        g.add_vertex(name=v)
vertices_ids = [v['name'] for v in g.vs]
fig, ax = plt.subplots(figsize=(5,5))
# use as layout the last positions in the cycle
i = configs0[-1]
imod = i*jumpTrajConfigs
df_single_config = dfconfigs.loc[(imod*Nbots):(imod*Nbots+Nbots-1)]
true_layout = []
for j in vertices_ids:
    x, y = float(df_single_config.loc[df_single_config['ID']==j]['x_position']), float(df_single_config.loc[df_single_config['ID']==j]['y_position'])
    true_layout.append([x,y])
true_layout = ig.Layout(true_layout)
ig.plot(
    g, target=ax, layout=true_layout, vertex_size = 1, vertex_color = 'steelblue', vertex_frame_width = 1.0, 
    vertex_frame_color = 'white'
)
circle = plt.Circle([0.0, 0.0], arena_r+exclusion_r, fill=False, edgecolor = 'k')
ax.add_patch(circle)
ax.set_xlim(-(arena_r+exclusion_r+1), arena_r+exclusion_r+1)
ax.set_ylim(-(arena_r+exclusion_r+1), arena_r+exclusion_r+1)
for j,v in enumerate(vertices_ids):
    coords = true_layout[j]
    circle = plt.Circle(tuple(coords), exclusion_r, color='xkcd:tan', alpha=0.5, clip_on = False)
    ax.add_patch(circle)
    # ax.text(coords[0], coords[1], f'{v}')
fig.savefig(f'integrated_config_cicle_{cicle}.png')
plt.close(fig)

#%%
# fig, ax = plt.subplots(figsize=(5,5))
# g = ig.Graph.DataFrame(dfcontactsINTcicle0[0:5], directed=False)
# ig.plot(g, target=ax, vertex_label=vertices_ids)
# plt.show()


#%%
# for e in g.es:
#     print(e.source, e.target)


# %%
