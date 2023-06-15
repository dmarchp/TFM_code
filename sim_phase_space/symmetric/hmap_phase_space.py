from sys import argv
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import subprocess
import numpy as np
from scipy import interpolate

if len(argv)==1:
    q1 = int(input("Enter the quality for site 1: "))
    q2 = int(input("Enter the quality for site 2: "))
    #model = str(input("Which model? (List/Galla) " ))
    ic = str(input("Initial condition? (N/P/Phard) "))
    N = int(input("Number of bots: "))
elif len(argv)==5:
    q1 = int(argv[1])
    q2 = int(argv[2])
    #model = str(argv[3])
    #ic = str(argv[4])
    ic = str(argv[3])
    N = int(argv[4])
else:
    print("Input parameter error. Execute as *.py q1 q2 ic Nbots or as *.py")
    exit()
    
# which model?
#if model in ["G", "Galla", "galla"]:
#    model = "Galla"
#elif model in ["L", "List", "list"]:
#    model = "List"
#else:
#    print("Incorrect model introduced, shuting down!")
#    exit()
# ALWAYS GALLA
model = "Galla"
    
# which initial condition?
if ic in ["N", "n", "uncomitted"]:
    ic = "N"
elif ic in ["P", "p", "pi"]:
    ic = "P"
elif ic in ["Phard", "phard", "p hard", "P hard", "Pi hard", "pi hard"]:
    ic = "Phard"
else:
    print("Incorrect initial condition, shuting down!")
    exit()
    
# input file (phase space):
# +'safe_every_5_pi/'
if_name = 'results/'+f'q1_{q1}_q2_{q2}_phase_space_{model}_ic_{ic}_Nbots_{N}.csv'
df_phase_space = pd.read_csv(if_name)

print("Creating phase space maps with the following parameters: ")
print(f"Site 1 quality: {q1}")
print(f"Site 2 quality: {q2}")
print(f"Model: {model}")
print(f"Initial conditions: {ic}")

# ticks for pi:
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
        
# ticks for lambda:
y_ticks = []
n = df_phase_space.groupby('pi')['lambda'].nunique().iloc[0]
if n==19: y_ticks = ['','','','',0.25,'','','','',0.5,'','','','',0.75,'','','','']     

def get_Tline_old(magnitud,df_to_map):
    if magnitud == 'Q':
        m_trsl = 'Q2'
    df_Tline = pd.read_csv(f'/home/david/Desktop/Uni_code/TFM_code/Qeq0_line/symmetric_pi/results/q_{q1}_{q2}/pi_lambda_{m_trsl}eq0.csv')
    #df_Tline = df_Tline[df_Tline['lambda'].str.strip() != 'Inf']
    df_Tline = df_Tline[~df_Tline['lambda'].str.contains('Inf')] # catches Inf, Infi, ..., Infinity
    df_Tline['lambda'] = pd.to_numeric(df_Tline['lambda']) # downcast="float" to make it float32
    df_Tline.reset_index(drop=True, inplace=True)
    # Reescale Tline and center to the heatmap squares:
    # pi es multiplica per 2 pq originalment esta entre 0 i 0.5
    df_Tline['pi'] = (df_Tline['pi'])*2*len(df_to_map.columns)-0.5
    df_Tline['lambda'] = (df_Tline['lambda'])*10*2-0.5
    #df_Tline2['lambda'] = (df_Tline2['lambda'])*(len(df_to_map))
    return df_Tline
    
def get_Tline(magnitud,df_to_map):
    if magnitud == 'Q':
        m_trsl = 'Q2'
    #q1=25
    #q2=30
    df_Tline = pd.read_csv(f'/home/david/Desktop/Uni_code/TFM_code/Qeq0_line/symmetric_pi/results/q_{q1}_{q2}/pi_lambda_{m_trsl}eq0.csv')
    rStrings = False
    for i in range(len(df_Tline)):
        #if (type(df_Tline['lambda'][i]) == 'str'):  BAD BAD BAAD!
        if(isinstance(df_Tline['lambda'][i], str)):
            rStrings = True
            #print(type(df_Tline['lambda'][i]))
    if rStrings:
        #df_Tline = df_Tline[df_Tline['lambda'].str.strip() != 'Inf']
        df_Tline = df_Tline[~df_Tline['lambda'].str.contains('Inf')] # catches Inf, Infi, ..., Infinity
        df_Tline['lambda'] = pd.to_numeric(df_Tline['lambda']) # downcast="float" to make it float32
        df_Tline.reset_index(drop=True, inplace=True)
    # Reescale Tline and center to the heatmap squares:
    # pi es multiplica per 2 pq originalment esta entre 0 i 0.5
  #  df_Tline['pi'] = (df_Tline['pi'])*2*len(df_to_map.columns)-0.5
    #df_Tline['lambda'] = (df_Tline['lambda'])*10*2-0.5
  #  df_Tline['lambda'] = (df_Tline['lambda'])*(len(df_to_map)+1)-0.5
    #df_Tline2['lambda'] = (df_Tline2['lambda'])*(len(df_to_map))
    return df_Tline          
            
            
def plot_hmap_complete(magnitud, vmin, vmax, cmap, interpolation=False, adjust_cbar=False, tline=False, show_vals=False, zeroRegion=False):
    # aixo es un pegote pq al simular no guardo aquest param ordre nou. Si canvio exec o el codi main py ho haure de treure:
    #if(magnitud=='m'):
    #    df_phase_space['m']=(3*df_phase_space['f2']-1)/2
    df_to_map = df_phase_space.pivot('lambda','pi',magnitud) # lambda rows, pi columns
    im_name = f'q1_{q1}_q2_{q2}_{magnitud}_hmap'
    # read hmap and carry out the interpolation:
    pi = df_phase_space['pi'].unique()
    lamb = df_phase_space['lambda'].unique()
    z = []
    for i,p in enumerate(pi):
        z.append([])
        for l in lamb:
            value = df_to_map.loc[l].loc[p]
            z[i].append(value)
    z=np.array(z)
    xgrid, ygrid = np.mgrid[min(pi):max(pi):complex(0,len(pi)), min(lamb):max(lamb):complex(0,len(lamb))]
    tck = interpolate.bisplrep(xgrid, ygrid, z)
    if(interpolation):
        model_label_pos = (0.0,0.93)
        ic_label_pos = (0.0,0.90)
        absQ_lt_label_pos = (0.0,0.87)
        im_name += '_spline'
        xnew, ynew = np.mgrid[min(pi):max(pi):complex(0,(max(pi)-min(pi))*100+1), min(lamb):max(lamb):complex(0,(max(lamb)-min(lamb))*100+1)]
        #pi_new = [round(x[0],2) for x in xnew]
        #lamb_new = [round(y,2) for y in ynew[0]]
        znew = interpolate.bisplev(xnew[:,0], ynew[0,:], tck)
        xax_grid, yax_grid, zplot = xnew, ynew, znew
    else:
        xax_grid, yax_grid, zplot = xgrid, ygrid, z
        model_label_pos = (-0.01,0.95)
        ic_label_pos = (0.0,0.90)
        absQ_lt_label_pos = (-0.025,0.85)
    # Overwrite the vmin,vmax values if adjust_cbar is true
    if(adjust_cbar):
        im_name += '_adjCbar'
        zmax = abs(z).max()
        zmin = abs(z).min()
        if(magnitud in ['f0', 'f1', 'f2']):
            vmax = zmax
            vmin = zmin
        else: # with Q, keep the map centered at zero (white)
            vmin = -zmax
            vmax = zmax
    if(zeroRegion):
        absQ_lt = 0.03
        zplot_ZR = np.copy(zplot)
        for i,xrow in enumerate(xax_grid):
            x = xrow[0]
            for yrow in yax_grid:
                for j,y in enumerate(yrow):
                    if(abs(zplot[i,j]) < absQ_lt):
                        zplot_ZR[i,j] = 1
                    else:
                        zplot_ZR[i,j] = 0
        im_name += '_zeroRegion'
    if(magnitud=='m'): # color the region where f0 is maximal
        zplot_ZR = np.copy(zplot)
        for i,xrow in enumerate(xax_grid):
            x = xrow[0]
            for yrow in yax_grid:
                for j,y in enumerate(yrow):
                    f0 = float(df_phase_space.loc[(df_phase_space['pi'] == 0.05) & (df_phase_space['lambda'] == 0.05)]['f0'])
                    f1 = float(df_phase_space.loc[(df_phase_space['pi'] == 0.05) & (df_phase_space['lambda'] == 0.05)]['f1'])
                    f2 = float(df_phase_space.loc[(df_phase_space['pi'] == 0.05) & (df_phase_space['lambda'] == 0.05)]['f2'])
                    if((f0 > f1) and (f0 > f2)):
                        zplot_ZR[i,j] = 1
                    elif((f0 > f1) and (f0 < f2)):
                        zplot_ZR[i,j] = 0.5
                    else:
                         zplot_ZR[i,j] = 0
    # plot the (interpolated) map:
    fig, ax = plt.subplots(figsize=(8,6))
    im = ax.pcolormesh(xax_grid, yax_grid, zplot, cmap=cmap, vmin=vmin, vmax=vmax, shading='auto')
    if(zeroRegion):
        ax.pcolormesh(xax_grid, yax_grid, np.where(zplot_ZR == 0, np.nan, zplot_ZR), cmap='binary', vmin=0, vmax=1, shading='auto', alpha=0.1)
    if(magnitud=='m'):
        ax.pcolormesh(xax_grid, yax_grid, zplot_ZR, cmap='binary', vmin=0, vmax=1, shading='auto', alpha=0.1)
    fig.colorbar(im, ax=ax)
    ax.set_xlabel(r"$\pi_{1,2}$")
    ax.set_ylabel(r"$\lambda$")
    # read and plot the theoretical line:
    if(tline):
        df_Tline = get_Tline(magnitud,df_to_map)
        if not(df_Tline.empty):
            min_l = yax_grid[0][0]
            index_from_a = list(df_Tline['pi']).index(xax_grid[0][0])
            index_from_b = 0
            for i,l in enumerate(list(df_Tline['lambda'])):
                if(l < min_l):
                    index_from_b = i + 1
            index_from = max([index_from_a,index_from_b])
            ax.plot(list(df_Tline['pi'])[index_from:], list(df_Tline['lambda'])[index_from:])
            im_name += '_Tline'
    # show the values of the heatmap:
    if(show_vals):
        xrow = []
        ycol = ygrid[0]
        for xcol in xgrid:
            xrow.append(xcol[0])
        for i in range(len(xrow)):
            for j in range(len(ycol)):
                if((i==1 and (j==3 or j==11)) or ((i==3 and (j==3 or j==11)))):
                    ax.text(xgrid[i,j],ygrid[i,j], '%.2f' % zplot[i,j], horizontalalignment='center',
                        verticalalignment='center', fontsize='small', fontweight='bold')
                else:
                    ax.text(xgrid[i,j],ygrid[i,j], '%.2f' % zplot[i,j], horizontalalignment='center',
                        verticalalignment='center', fontsize='small')
        im_name += '_ShowVals'
    plt.text(model_label_pos[0],model_label_pos[1],f"{model}",fontsize="small")
    plt.text(ic_label_pos[0],ic_label_pos[1],f"{ic}",fontsize="small")
    if(zeroRegion):
        plt.text(absQ_lt_label_pos[0],absQ_lt_label_pos[1],rf"$Q < |{absQ_lt}|$",fontsize="x-small")
    im_name += f"_{model}_ic_{ic}_Nbots_{N}"
    im_name += '.png'
    plt.savefig(im_name, bbox_inches='tight', pad_inches=0.01)
    
#plot_hmap('Q', -1, 1, 'RdBu', tline=True)
#plot_hmap('f2', 0, 1, 'viridis')

#tline_flag=input("Plot tline in consensus map? (y/n) ")
#if(tline_flag.lower()=='y'):
#    tline_flag = True
#else:
#    tline_flag = False

tline_flag = True

#plot_hmap_complete('Q', -1, 1, 'RdBu', tline=tline_flag)
#plot_hmap_complete('Q', -1, 1, 'RdBu', tline=tline_flag, show_vals=True)
#plot_hmap_complete('Q', -1, 1, 'RdBu', tline=tline_flag, zeroRegion=True)
#plot_hmap_complete('Q', -1, 1, 'RdBu', tline=tline_flag, interpolation=True, zeroRegion=True)
plot_hmap_complete('Q', -1, 1, 'RdBu', tline=tline_flag, interpolation=True)
##plot_hmap_complete('Q', -1, 1, 'RdBu', tline=tline_flag, interpolation=True, adjust_cbar=True)

##plot_hmap_complete('f2', 0, 1, 'magma', interpolation=True, adjust_cbar=True)

#plot_hmap_complete('f0', 0, 1, 'Reds', interpolation=False, adjust_cbar=True, show_vals=True)
#plot_hmap_complete('f1', 0, 1, 'Greens', interpolation=False, adjust_cbar=True, show_vals=True)
#plot_hmap_complete('f2', 0, 1, 'Blues', interpolation=False, adjust_cbar=True, show_vals=True)

plot_hmap_complete('f0', 0, 1, 'Reds', interpolation=True, adjust_cbar=True)
plot_hmap_complete('f1', 0, 1, 'Greens', interpolation=True, adjust_cbar=True)
plot_hmap_complete('f2', 0, 1, 'Blues', interpolation=True, adjust_cbar=True)

#plot_hmap_complete('m',0,1,'Spectral')
#plot_hmap_complete('k2',0,1,'plasma')

#plot_hmap_complete('sdf2', 0, 0.13, 'inferno')

#subprocess.call(f"mkdir -p plots/q_{q1}_{q2}", shell=True)
#subprocess.call(f"mv *.png plots/q_{q1}_{q2}", shell=True)
