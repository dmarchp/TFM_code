import matplotlib.pyplot as plt
import pandas as pd
from numpy import linspace

arena_r = 20
model = 'Galla'
N = 35
df = pd.read_csv(f"{model}/{N}_bots/degree_average.csv")
df = df.loc[df['arena_r']==20]
fig, ax = plt.subplots()
ax.plot(df['interac_r'], df['mean_degree'])
ax.set_xlabel('interaction radius (cm)')
ax.set_ylabel('average bot degree')
fig.text(0.1,0.97, f'$N = {N}, \; a_r = {arena_r}$')
fig.tight_layout()
fig.savefig(f'average_degree_N_{N}_ar_{arena_r}.png')
plt.close(fig)


#interac_r_list = [2,4,6,8,10,14,18,22,30]
interac_r_list = [2,4,6,8,10,14,18,22,30]
colors = plt.cm.gist_rainbow(linspace(0,1,len(interac_r_list)))
fig, ax = plt.subplots()
for i,ir in enumerate(interac_r_list):
    df = pd.read_csv(f"{model}/{N}_bots/degree_probs/degree_probs_ar_{arena_r}_ir_{ir}.csv")
    ax.plot(df['degree'], df['prob'], color=colors[i], label=f'{ir}')
ax.set_xlabel('degree')
ax.set_ylabel('P(degree)')
fig.legend(title='$i_r$')
fig.text(0.1,0.97, f'$N = {N}, \; a_r = {arena_r}$')
fig.tight_layout()
fig.savefig(f'degree_prob_N_{N}_ar_{arena_r}.png')
plt.close(fig)



