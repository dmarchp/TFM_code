from sys import argv
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import subprocess
import numpy as np

if len(argv)==1:
    q1 = int(input("Enter the quality for site 1: "))
    q2 = int(input("Enter the quality for site 2: "))
    l = float(input("Enter the interdependence: "))
elif len(argv)==4:
    q1 = int(argv[1])
    q2 = int(argv[2])
    l = float(argv[3])
else:
    print("Input parameter error. Execute as *.py q1 q2 l or as *.py")
    exit()
    
lstr = str(l)
lstr = lstr[2:]
if (l*100)%10 == 0:
    lstr = lstr+'0'
    
# input file (phase space):
if_name = 'results/'+f'lambda_{lstr}/'+f'q1_{q1}_q2_{q2}_l_{lstr}_phase_space.csv'
df_phase_space = pd.read_csv(if_name)

print("Creating phase space (pi1, pi2) maps with the following parameters: ")
print(f"Site 1 quality: {q1}")
print(f"Site 2 quality: {q2}")
print(f"Interdependence: {l}")

# ticks for pi1, pi2:
#x_ticks = ['',0.1,'',0.2,'',0.3,'',0.4,'',0.5]
x_ticks = []
n = df_phase_space.groupby('lambda')['pi'].nunique().iloc[0]
if n==10: every = 2
if n==50: every = 10
for i in range(1,n+1):
    if(i%every==0):
        x_ticks.append(i/(every*10))
    else:
        x_ticks.append('')


def get_Tline(magnitud,df_to_map):
    if magnitud == 'Q':
        m_trsl = 'Q2'
    df_Tline = pd.read_csv(f'/home/david/Desktop/Uni_code/TFM_code/Qeq0_line/asymmetric_pi/results/lambda_{lstr}/q_{q1}_{q2}/pi1_pi2_{m_trsl}eq0.csv')
    #df_Tline = df_Tline[df_Tline['pi2'].str.strip() != 'Inf']
    df_Tline = df_Tline[~df_Tline['pi2'].str.contains('Inf')] # catches Inf, Infi, ..., Infinity
    df_Tline["pi2"] = pd.to_numeric(df_Tline["pi2"]) # downcast="float" to make it float32
    df_Tline.reset_index(drop=True, inplace=True)
    # Reescale Tline and center to the heatmap squares:
    # pi es multiplica per 2 pq originalment esta entre 0 i 0.5
    df_Tline['pi1'] = (df_Tline['pi1'])*2*len(df_to_map.columns)-0.5
    df_Tline['pi2'] = (df_Tline['pi2'])*2*len(df_to_map.columns)-0.5
    return df_Tline

def plot_hmap(magnitud, vmin, vmax, cmap, tline=False):
    df_to_map = df_phase_space.pivot('pi2','pi1',magnitud) # pi2 rows, p1 columns
    fig, ax = plt.subplots()
    if(x_ticks):
        sns.heatmap(df_to_map, vmin=vmin,vmax=vmax, cmap=cmap, ax=ax, xticklabels=x_ticks, yticklabels=x_ticks)
    else:
        sns.heatmap(df_to_map, vmin=vmin,vmax=vmax, cmap=cmap, ax=ax)
    ax.invert_yaxis()
    ax.set_xlabel(r"$\pi_{1}$")
    ax.set_ylabel(r"$\pi_{2}$")
    #fig.tight_layout()
    if(tline):
        df_Tline = get_Tline(magnitud,df_to_map)
        sns.lineplot(x=df_Tline['pi1'], y=df_Tline['pi2'], color='black')
        plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap_wTline.png', bbox_inches='tight', pad_inches=0.01)
    else:
        plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap.png', bbox_inches='tight', pad_inches=0.01)
    
plot_hmap('Q', -1, 1, 'RdBu', tline=True)
plot_hmap('f2', 0, 1, 'viridis')

subprocess.call(f"mkdir -p plots/lambda_{lstr}/q_{q1}_{q2}", shell=True)
subprocess.call(f"mv *.png plots/lambda_{lstr}/q_{q1}_{q2}", shell=True)


