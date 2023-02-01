#%%
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt

# everything in milimeters
arena_r = 750.0
exclusion_r = 15.0
interac_r = 70.0
cicle = 11

N = 492

# csv files:
# filenameConfig = f'raw_json_files/RWDIS_mod/configs/PRW_nBots_{N}_ar_{arena_r/10}_speed_9_speedVar_2_001.csv'
# filenameContact = f'raw_json_files/RWDIS_mod/configs/contacts/PRW_nBots_{N}_ar_{arena_r/10}_speed_9_speedVar_2_001_loops_800_ir_70.0_contacts.csv'
# dfconfigs = pd.read_csv(filenameConfig)
# dfcontacts = pd.read_csv(filenameContact)

# parquet files:
filenameConfig = f'raw_json_files/RWDIS_mod/configs/PRW_nBots_{N}_ar_{arena_r/10}_speed_9_speedVar_2_001.parquet'
filenameContact = f'raw_json_files/RWDIS_mod/configs/contacts/PRW_nBots_{N}_ar_{arena_r/10}_speed_9_speedVar_2_001_loops_800_ir_70.0_contacts.parquet'
dfconfigs = pd.read_parquet(filenameConfig)
dfcontacts = pd.read_parquet(filenameContact)


ids = pd.unique(dfconfigs['ID'])
Nbots = len(ids)
dfcicle0 = dfcontacts.loc[dfcontacts['cicleID']==cicle]
configs0 = pd.unique(dfcicle0['configID'])

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
    df_single_config = dfconfigs.loc[(i*Nbots):(i*Nbots+Nbots-1)]
    true_layout = []
    vertices_ids = [v['name'] for v in g.vs]
    for j in vertices_ids:
        x, y = float(df_single_config.loc[df_single_config['ID']==j]['x_position']), float(df_single_config.loc[df_single_config['ID']==j]['y_position'])
        true_layout.append([x,y])
    true_layout = ig.Layout(true_layout)
    fig, ax = plt.subplots(figsize=(5,5))
    ig.plot(
        g, target=ax, layout=true_layout, vertex_size = 2, vertex_color = 'steelblue', vertex_frame_width = 1.0, 
        vertex_frame_color = 'white'
    )
    circle = plt.Circle([0.0, 0.0], arena_r, fill=False, edgecolor = 'k')
    ax.add_patch(circle)
    ax.set_xlim(-(arena_r+1), arena_r+1)
    ax.set_ylim(-(arena_r+1), arena_r+1)
    fig.suptitle(f'config {i} in cycle {cicle}')
    for j,v in enumerate(vertices_ids):
        coords = true_layout[j]
        circle = plt.Circle(tuple(coords), exclusion_r, color='xkcd:purple', alpha=0.5, clip_on = False)
        ax.add_patch(circle)
        # ax.text(coords[0], coords[1], f'{v}')
    # extra: show interaction radius for onne bot
    circle = plt.Circle(true_layout[0], interac_r, fill=False, edgecolor='xkcd:grey', ls='--')
    ax.add_patch(circle)
    fig.savefig(f'config_{str(i).zfill(3)}_cicle_{cicle}.png')
    plt.close(fig)

#%%
# print the corresponding integrated config:
filenameContactInt = f'raw_json_files/RWDIS_mod/configs/contacts/PRW_nBots_{N}_ar_{arena_r/10}_speed_9_speedVar_2_002_loops_800_ir_70.0_contacts_cicleINT.csv'
dfcontactsINT = pd.read_csv(filenameContactInt)
dfcontactsINTcicle0 = dfcontactsINT.loc[dfcontactsINT['cicleID']==1].copy(deep=True)
dfcontactsINTcicle0.drop(labels='cicleID', axis='columns', inplace=True)
# dfcontactsINTcicle0.sort_values(by=['contacts0', 'contacts1'], inplace=True)
# dfcontactsINTcicle0.reset_index(drop=True, inplace=True)
g = ig.Graph.DataFrame(dfcontactsINTcicle0, directed=False)
if g.vcount() < Nbots:
    print('here')
    vertices_ids = [v['name'] for v in g.vs]
    lacking_vertices = [v for v in range(Nbots) if v not in vertices_ids]
    for v in lacking_vertices:
        g.add_vertex(name=v)
vertices_ids = [v['name'] for v in g.vs]
fig, ax = plt.subplots(figsize=(5,5))
# use as layout the last positions in the cycle
i = configs0[-1]
df_single_config = dfconfigs.loc[(i*Nbots):(i*Nbots+Nbots-1)]
true_layout = []
for j in vertices_ids:
    x, y = float(df_single_config.loc[df_single_config['ID']==j]['x_position']), float(df_single_config.loc[df_single_config['ID']==j]['y_position'])
    true_layout.append([x,y])
true_layout = ig.Layout(true_layout)
ig.plot(
    g, target=ax, layout=true_layout, vertex_size = 1, vertex_color = 'steelblue', vertex_frame_width = 1.0, 
    vertex_frame_color = 'white'
)
circle = plt.Circle([0.0, 0.0], arena_r, fill=False, edgecolor = 'k')
ax.add_patch(circle)
ax.set_xlim(-(arena_r+1), arena_r+1)
ax.set_ylim(-(arena_r+1), arena_r+1)
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
