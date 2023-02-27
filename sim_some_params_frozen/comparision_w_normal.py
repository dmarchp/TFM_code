import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

q1 = 2
q2s = [3, 4, 5]

#q1 = 3
#q2s = [4, 5, 6]

#q1 = 4
#q2s = [5, 6, 7]

pi1 = 0.1
pi2 = 0.1
l = 0.8

model_folder = 'Galla/'
#model_folder = 'List/'

# CREA EL DATAFRAME AMB ELS RESULTATS DE SIMULACIONS MEAN FIELD
df1 = pd.read_csv(f'../sim_some_params/{model_folder}stationary_dfs/stat_values_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2s[0]}_l_{l}.csv', index_col=0)
df2 = pd.read_csv(f'../sim_some_params/{model_folder}stationary_dfs/stat_values_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2s[1]}_l_{l}.csv', index_col=0)
df3 = pd.read_csv(f'../sim_some_params/{model_folder}stationary_dfs/stat_values_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2s[2]}_l_{l}.csv', index_col=0)

df1['Q'] = df1['f2']-2*df1['f1']
df2['Q'] = df2['f2']-2*df2['f1']
df3['Q'] = df3['f2']-2*df3['f1']

# com unir els dfs per fer servir hue al boxplot:
# https://stackoverflow.com/questions/44162416/how-to-join-pandas-dataframe-so-that-seaborn-boxplot-or-violinplot-can-use-a-col

df1['q2'] = 3
df2['q2'] = 4
df3['q2'] = 5

df4 = pd.concat([df1.melt(id_vars='q2', var_name='f'),
                 df2.melt(id_vars='q2', var_name='f'),
                 df3.melt(id_vars='q2', var_name='f')],
                 ignore_index=True)
                

# CREA EL DATAFRAME PER LES SIMULACIONS AMB FROZEN POSITION
df1 = pd.read_csv(f'{model_folder}stationary_dfs/stat_values_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2s[0]}_l_{l}.csv', index_col=0)
df2 = pd.read_csv(f'{model_folder}stationary_dfs/stat_values_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2s[1]}_l_{l}.csv', index_col=0)
df3 = pd.read_csv(f'{model_folder}stationary_dfs/stat_values_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2_{q2s[2]}_l_{l}.csv', index_col=0)

df1['Q'] = df1['f2']-2*df1['f1']
df2['Q'] = df2['f2']-2*df2['f1']
df3['Q'] = df3['f2']-2*df3['f1']

# com unir els dfs per fer servir hue al boxplot:
# https://stackoverflow.com/questions/44162416/how-to-join-pandas-dataframe-so-that-seaborn-boxplot-or-violinplot-can-use-a-col

df1['q2'] = 3
df2['q2'] = 4
df3['q2'] = 5

df4_fp = pd.concat([df1.melt(id_vars='q2', var_name='f'),
                 df2.melt(id_vars='q2', var_name='f'),
                 df3.melt(id_vars='q2', var_name='f')],
                 ignore_index=True)



fig, ax = plt.subplots(dpi=200)
ax = sns.boxplot(x='f', y='value', hue='q2', order=['f0','f1','f2'], data=df4_fp, linewidth=0.7, fliersize=0.7)
ax = sns.boxplot(x='f', y='value', hue='q2', order=['f0','f1','f2'], data=df4, linewidth=0.5, fliersize=0.5)

figQ, axQ = plt.subplots()
axQ = sns.boxplot(x='f', y='value', hue='q2', order=['Q', ], data=df4_fp, linewidth=0.7, fliersize=0.7)
axQ = sns.boxplot(x='f', y='value', hue='q2', order=['Q', ], data=df4, linewidth=0.7, fliersize=0.5)

#ax = sns.boxplot(x='f', y='value', hue='q2', data=df4_fp, whiskerprops = dict(color='black', linewidth=0.7),
#                 capprops = dict(color='black', linewidth=0.7), boxprops = dict(linestyle='-', linewidth=0.7),
#                 flierprops = dict(color='green'), fliersize=0.7)
                 
# SET ADJUSTMENTS FOR THE FROZEN POSITION BOX N WHISKERS
# https://stackoverflow.com/questions/36305695/assign-a-color-to-a-specific-box-in-seaborn-boxplot
ax.artists[0].set_color('red')
ax.artists[0].set_alpha(0.4)
ax.artists[1].set_color('red')
ax.artists[1].set_alpha(0.7)
ax.artists[2].set_color('red')

ax.artists[3].set_color('green')
ax.artists[3].set_alpha(0.4)
ax.artists[4].set_color('green')
ax.artists[4].set_alpha(0.7)
ax.artists[5].set_color('green')

ax.artists[6].set_color('blue')
ax.artists[6].set_alpha(0.4)
ax.artists[7].set_color('blue')
ax.artists[7].set_alpha(0.7)
ax.artists[8].set_color('blue')

axQ.artists[0].set_color('xkcd:purple')
axQ.artists[0].set_alpha(0.4)
axQ.artists[1].set_color('xkcd:purple')
axQ.artists[1].set_alpha(0.7)
axQ.artists[2].set_color('xkcd:purple')

#for i in range(len(ax.lines[:])):
#    ax.lines[i].set_color('black')
#    ax.lines[i].set_linewidth(0.7)

for line in ax.lines[:int(len(ax.lines)/2)+1]:
    line.set_color('black')
    line.set_linewidth(0.7)
    
for line in axQ.lines[:int(len(axQ.lines)/2)+1]:
    line.set_color('black')
    line.set_linewidth(0.7)
    
#for i in range(len(ax.artists)):
#    ax.artists[i].set_edgecolor('black')
#for art in ax.artists[:int(len(ax.artists)/2)+1]:
#    art.set_edgecolor('black')

# SET ADJUSTMENTS FOR THE MEAN FIELD BOX N WHISKERS
ax.artists[9].set_color('red')
ax.artists[9].set_alpha(0.2)
ax.artists[10].set_color('red')
ax.artists[10].set_alpha(0.2)
ax.artists[11].set_color('red')
ax.artists[11].set_alpha(0.2)

ax.artists[12].set_color('green')
ax.artists[12].set_alpha(0.2)
ax.artists[13].set_color('green')
ax.artists[13].set_alpha(0.2)
ax.artists[14].set_color('green')
ax.artists[14].set_alpha(0.2)

ax.artists[15].set_color('blue')
ax.artists[15].set_alpha(0.2)
ax.artists[16].set_color('blue')
ax.artists[16].set_alpha(0.2)
ax.artists[17].set_color('blue')
ax.artists[17].set_alpha(0.2)

axQ.artists[3].set_color('xkcd:purple')
axQ.artists[3].set_alpha(0.2)
axQ.artists[4].set_color('xkcd:purple')
axQ.artists[4].set_alpha(0.2)
axQ.artists[5].set_color('xkcd:purple')
axQ.artists[5].set_alpha(0.2)

for line in ax.lines[int(len(ax.lines)/2)+1:]:
    line.set_color('orange')
    line.set_linewidth(0.5)
    
for line in axQ.lines[int(len(axQ.lines)/2)+1:]:
    line.set_color('orange')
    line.set_linewidth(0.5)
                 
ax.get_legend().remove()
ax.set(xlabel=None)  # remove the axis label
ax.set(ylabel=None)  # remove the axis label

axQ.get_legend().remove()
axQ.set(xlabel=None)  # remove the axis label
axQ.set(ylabel=None)  # remove the axis label

    
ax.grid(axis='y', which='major', color='xkcd:gray', linestyle='--', alpha=0.5)
    
ax.set_title(rf'{model_folder[:-1]} $\pi_1 = {pi1}, \; \pi_2 = {pi2}, \; q_1 = {q1}, \; q_2 = ({q2s[0]}, {q2s[1]}, {q2s[2]}), \; \lambda = {l}$')
fig.savefig(f'box_plot_freqs_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2s_l_{l}_{model_folder[:-1]}.png', bbox_inches='tight', pad_inches=0.05)

axQ.grid(axis='y', which='major', color='xkcd:gray', linestyle='--', alpha=0.5)
axQ.set_title(rf'{model_folder[:-1]} $\pi_1 = {pi1}, \; \pi_2 = {pi2}, \; q_1 = {q1}, \; q_2 = ({q2s[0]}, {q2s[1]}, {q2s[2]}), \; \lambda = {l}$')
#figQ.tight_layout()
figQ.savefig(f'box_plot_Q_pi1_{pi1}_pi2_{pi2}_q1_{q1}_q2s_l_{l}_{model_folder[:-1]}.png', bbox_inches='tight', pad_inches=0.05)
