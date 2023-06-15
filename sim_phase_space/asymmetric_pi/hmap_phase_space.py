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
    l = float(input("Enter the interdependence: "))
    #model = str(input("Which model do you want to simulate? (List/Galla) "))
    ic = str(input("Which initial conditions? (no (uncomitted), pi, pi hard) (N/P/Phard) "))
    N = int(input("Number of bots: "))
elif len(argv)==6:
    q1 = int(argv[1])
    q2 = int(argv[2])
    l = float(argv[3])
    #model = str(argv[4])
    #ic = str(argv[5])
    ic = str(argv[4])
    N = int(argv[5])
else:
    print("Input parameter error. Execute as *.py q1 q2 l or as *.py")
    exit()
    
# which model?
#if model in ["G", "Galla", "galla"]:
#    model = "Galla"
#elif model in ["L", "List", "list"]:
#    model = "List"
#else:
#    print("Incorrect model introduced, shuting down!")
#    exit()
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
    
lstr = str(l)
lstr = lstr[2:]
if (l*100)%10 == 0:
    lstr = lstr+'0'
    
# input file (phase space):
if_name = 'results/'+f'lambda_{lstr}/'+f'q1_{q1}_q2_{q2}_l_{lstr}_phase_space_{model}_ic_{ic}_Nbots_{N}.csv'
df_phase_space = pd.read_csv(if_name)

print("Creating phase space (pi1, pi2) maps with the following parameters: ")
print(f"Site 1 quality: {q1}")
print(f"Site 2 quality: {q2}")
print(f"Interdependence: {l}")
print(f"Model: {model}")
print(f"Initial conditions: {ic}")

def get_Tline(magnitud,df_to_map):
    if magnitud == 'Q':
        m_trsl = 'Q2'
        m_trsl_2 = 'Q2s'
    df_Tline = pd.read_csv(f'/home/david/Desktop/Uni_code/TFM_code/Qeq0_line/asymmetric_pi/results/lambda_{lstr}/q_{q1}_{q2}/pi1_pi2_{m_trsl}eq0.csv')
    df_Tline_2 =  pd.read_csv(f'/home/david/Desktop/Uni_code/TFM_code/Qeq0_line/asymmetric_pi/results/lambda_{lstr}/q_{q1}_{q2}/pi1_pi2_{m_trsl_2}eq0.csv')
    rStrings = False
    for i in range(len(df_Tline)):
        if(isinstance(df_Tline['pi2'][i], str)):
            rStrings = True
            break
            #print(type(df_Tline['lambda'][i]))
    if rStrings:
        df_Tline = df_Tline[~df_Tline['pi2'].str.contains('Inf')] # catches Inf, Infi, ..., Infinity
        df_Tline['pi2'] = pd.to_numeric(df_Tline['pi2']) # downcast="float" to make it float32
        df_Tline.reset_index(drop=True, inplace=True)
    # repeat for the second line
    rStrings = False
    for i in range(len(df_Tline_2)):
        if(isinstance(df_Tline_2['pi2'][i], str)):
            rStrings = True
            break
    if rStrings:
        df_Tline_2 = df_Tline_2[~df_Tline_2['pi2'].str.contains('Inf')]
        df_Tline_2['pi2'] = pd.to_numeric(df_Tline_2['pi2'])
        df_Tline_2.reset_index(drop=True, inplace=True)
    return df_Tline, df_Tline_2
            
# plot hmap with options: 
# - piSumCondition (either a fixed value or a interval)
# https://stackoverflow.com/questions/64036309/is-it-possible-to-leave-blank-spaces-in-matplotlibs-pcolormesh-plots
# - interpolation (interpolate the data from sims to get a smooth heatmap)
# - adjust_cbar (get the max abs value from the map and set the max value of the colorbar to it)
# - tline (plot the line that predicts the transition bt Q<0 to Q>0)
def plot_hmap_complete(magnitud, vmin, vmax, cmap, piSumCondition=None, interpolation=False, adjust_cbar=False, tline=False, show_vals=False, zeroRegion=False):
    df_to_map = df_phase_space.pivot('pi2','pi1',magnitud) # pi1 rows, pi2 columns
    im_name = f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap'
    # check that input pisumcondition is given and is correct:
    if(piSumCondition):
        if(isinstance(piSumCondition,float)):
            piSumC_lb = piSumCondition # lower bound, lb
            piSumC_ub = piSumCondition # upper bound, ub
        elif(isinstance(piSumC,list) or isinstance(piSumC,tuple) or isinstance(piSumC,set)):
            piSumC_lb = piSumCondition[0] # lower bound, lb
            piSumC_ub = piSumCondition[1] # upper bound, ub
        else:
            print('Wrong piSumCondition, exiting function')
            exit()
        im_name += '_piSumC'
    # read hmap (and carry out the interpolation):
    pi1 = df_phase_space['pi1'].unique()
    pi2 = df_phase_space['pi2'].unique()
    z = []
    for i,p1 in enumerate(pi1):
        z.append([])
        for p2 in pi2:
            value = df_to_map.loc[p2].loc[p1]
            z[i].append(value)
    z=np.array(z)
    xgrid, ygrid = np.mgrid[min(pi1):max(pi1):complex(0,len(pi1)), min(pi2):max(pi2):complex(0,len(pi2))]
    # interpolation steps:
    if(interpolation):
        tck = interpolate.bisplrep(xgrid, ygrid, z)
        xnew, ynew = np.mgrid[min(pi1):max(pi1)+0.01:complex(0,(max(pi1)-min(pi1))*100+1), min(pi2):max(pi2)+0.01:complex(0,(max(pi2)-min(pi2))*100+1)] # 0.01, 0.02, 0.03, ..., 0.49, 0.50; per això el max(pi1)+0.01
        znew = interpolate.bisplev(xnew[:,0], ynew[0,:], tck)
        xax_grid, yax_grid = xnew, ynew
        zplot = znew
        im_name += '_spline'
    else:
        xax_grid, yax_grid = xgrid, ygrid
        zplot = z
    # get only the piSumConditions:
    if(piSumCondition):
        for i,xrow in enumerate(xax_grid):
            x = xrow[0]
            for yrow in yax_grid:
                for j,y in enumerate(yrow):
                    if not (round(x+y,2) >= piSumC_lb and round(x+y,2) <= piSumC_ub):
                        zplot[i,j] = 0.0
    # Get the experimental region where the parameter is zero:
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
    # Overwrite the vmin,vmax values if adjust_cbar is true
    if(adjust_cbar):
        zmax = abs(zplot).max()
        zmin = abs(z).min()        
        if(magnitud in ['f0', 'f1', 'f2']):
            vmax = zmax
            vmin = zmin
        else: # with Q, keep the map centered at zero (white)
            vmin = -zmax
            vmax = zmax
        im_name += '_adjCbar'
    # plot the consensus map:
    fig, ax = plt.subplots(figsize=(8,6))
    if(piSumCondition):
        im = ax.pcolormesh(xax_grid, yax_grid, np.where(zplot == 0, np.nan, zplot), cmap=cmap, vmin=vmin, vmax=vmax, shading='auto')
    else:
        im = ax.pcolormesh(xax_grid, yax_grid, zplot, cmap=cmap, vmin=vmin, vmax=vmax, shading='auto')
    if(zeroRegion):
        ax.pcolormesh(xax_grid, yax_grid, np.where(zplot_ZR == 0, np.nan, zplot_ZR), cmap='binary', vmin=0, vmax=1, shading='auto', alpha=0.1)
    fig.colorbar(im, ax=ax)
    ax.set_xlabel(r"$\pi_{1}$")
    ax.set_ylabel(r"$\pi_{2}$")
    # read and plot the theoretical line:
    if(tline):
        df_Tline, df_Tline_2 = get_Tline(magnitud,df_to_map)
        im_name += '_Tline'
        if not(df_Tline_2.empty):
            index_from = 0
            ax.plot(list(df_Tline_2['pi1'])[index_from:], list(df_Tline_2['pi2'])[index_from:], '--', color='xkcd:navy blue')
        if not(df_Tline.empty):
            #print(df_Tline)
            #index_from = list(df_Tline['pi1']).index(xnew[0][0])
            index_from = 0
            ax.plot(list(df_Tline['pi1'])[index_from:], list(df_Tline['pi2'])[index_from:], color='xkcd:navy blue')
    if(show_vals):
        xrow = []
        ycol = ygrid[0]
        for xcol in xgrid:
            xrow.append(xcol[0])
        for i in range(len(xrow)):
            for j in range(len(ycol)):
                if(i%2==0 and j%2==0):
                    ax.text(xgrid[i,j],ygrid[i,j], '%.2f' % zplot[i,j], horizontalalignment='center',
                        verticalalignment='center', fontsize='xx-small')
        im_name += '_ShowVals'
    plt.text(-0.04,0.45,f"{model}",fontsize="small")
    plt.text(-0.03,0.43,f"{ic}",fontsize="small")
    if(zeroRegion):
        plt.text(-0.05,0.47,rf"$|Q|<{absQ_lt}$",fontsize="x-small")
    plt.text(-0.04,0.37,rf"$q_1 = {q1}$",fontsize="x-small")
    plt.text(-0.04,0.35,rf"$q_2 = {q2}$",fontsize="x-small")
    plt.text(-0.04,0.33,rf"$\lambda = {l}$",fontsize="x-small")
    im_name += f"_{model}_{ic}"
    im_name += '.png'
    plt.savefig(im_name, bbox_inches='tight', pad_inches=0.01)
            

#plot_hmap_complete('Q', -1, 1, 'RdBu') # standard plot, right out the data file
#plot_hmap_complete('Q', -1, 1, 'RdBu', interpolation=True, tline=True)
#plot_hmap_complete('Q', -1, 1, 'RdBu', piSumCondition=0.2, interpolation=True, adjust_cbar=True, tline=False)
plot_hmap_complete('Q', -1, 1, 'RdBu', tline=True)
#plot_hmap_complete('Q', -1, 1, 'RdBu', tline=True, zeroRegion=True)

#plot_hmap_complete('f0', 0, 1, 'Reds', adjust_cbar=True)
#plot_hmap_complete('f1', 0, 1, 'Greens', adjust_cbar=True)
#plot_hmap_complete('f2', 0, 1, 'Blues', adjust_cbar=True)
plot_hmap_complete('f0', 0, 1, 'Reds')
plot_hmap_complete('f1', 0, 1, 'Greens')
plot_hmap_complete('f2', 0, 1, 'Blues')

#plot_hmap_complete('f0', 0, 1, 'Reds', interpolation=True, adjust_cbar=True)
#plot_hmap_complete('f1', 0, 1, 'Greens', interpolation=True, adjust_cbar=True)
#plot_hmap_complete('f2', 0, 1, 'Blues', interpolation=True, adjust_cbar=True)

#plot_hmap_complete('f0', 0, 1, 'Reds', adjust_cbar=True, show_vals=True)
#plot_hmap_complete('f1', 0, 1, 'Greens', adjust_cbar=True, show_vals=True)
#plot_hmap_complete('f2', 0, 1, 'Blues', adjust_cbar=True, show_vals=True)

subprocess.call(f"mkdir -p plots/lambda_{lstr}/q_{q1}_{q2}", shell=True)
subprocess.call(f"mv *.png plots/lambda_{lstr}/q_{q1}_{q2}", shell=True)
