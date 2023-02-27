import pandas as pd
import matplotlib.pyplot as plt
from numpy import linspace
from scipy.ndimage import gaussian_filter1d
from graph_properties_functions import *
from collections import Counter
from scipy.optimize import curve_fit
import os
import subprocess
import glob

model = 'Galla'

pis = [0.3, 0.3]
qs = [7, 10]
arena_r = 20.0
exclusion_r = 1.5
interac_r = 7.0
N = 35

#colors = plt.cm.gist_rainbow(linspace(0,1,2))
colors = ['xkcd:turquoise', 'xkcd:brick red'] # push / no push!!!!!

# ----------------------------------------- SIMULATION RESULTS ----------------------------------------------------
def getSimResDf():
    # df push
    dfp = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}.csv')
    dfp = dfp.loc[(dfp['arena_r'] == arena_r) & (dfp['interac_r'] == interac_r) & (dfp['pi1'] == pis[0]) & (dfp['pi2'] == pis[1]) & (dfp['q1'] == qs[0]) & (dfp['q2'] == qs[1])]
    # df no push
    dfnp = pd.read_csv(f'{model}/{N}_bots/sim_fp_results_er_{exclusion_r}_NOPUSH.csv')
    dfnp = dfnp.loc[(dfnp['arena_r'] == arena_r) & (dfnp['interac_r'] == interac_r) & (dfnp['pi1'] == pis[0]) & (dfnp['pi2'] == pis[1]) & (dfnp['q1'] == qs[0]) & (dfnp['q2'] == qs[1])]
    return dfp, dfnp



# Figure: (x-lambda, y-fs) for push / no push
def plotSimResults_xl_yfs(dfp,dfnp):
    fig,ax = plt.subplots(1,3,figsize=(9,5))
    # push
    ax[1].plot(dfp['lambda'], dfp['f1'], color=colors[0])
    ax[2].plot(dfp['lambda'], dfp['f2'], color=colors[0])
    ax[0].plot(dfp['lambda'], dfp['f0'], label='push', color=colors[0])
    #ax[0].fill_between(dfp['lambda'], dfp['f0']-dfp['sdf0'], dfp['f0']+dfp['sdf0'], color=colors[0], alpha=0.3)
    #ax[1].fill_between(dfp['lambda'], dfp['f1']-dfp['sdf1'], dfp['f1']+dfp['sdf1'], color=colors[0], alpha=0.3)
    #ax[2].fill_between(dfp['lambda'], dfp['f2']-dfp['sdf2'], dfp['f2']+dfp['sdf2'], color=colors[0], alpha=0.3)
    # no push
    ax[0].plot(dfnp['lambda'], dfnp['f0'], label='no push', color=colors[1])
    ax[1].plot(dfnp['lambda'], dfnp['f1'], color=colors[1])
    ax[2].plot(dfnp['lambda'], dfnp['f2'], color=colors[1])
    # ax[0].fill_between(dfnp['lambda'], dfnp['f0']-dfnp['sdf0'], dfnp['f0']+dfnp['sdf0'], color=colors[1], alpha=0.3)
    # ax[1].fill_between(dfnp['lambda'], dfnp['f1']-dfnp['sdf1'], dfnp['f1']+dfnp['sdf1'], color=colors[1], alpha=0.3)
    # ax[2].fill_between(dfnp['lambda'], dfnp['f2']-dfnp['sdf2'], dfnp['f2']+dfnp['sdf2'], color=colors[1], alpha=0.3)
    ax[1].set_xlabel(r'$\lambda$')
    ax[0].set_ylabel(r'$f_0$')
    ax[1].set_ylabel(r'$f_1$')
    ax[2].set_ylabel(r'$f_2$')
    ax[0].legend()
    fig.text(0.05, 0.98, rf'N = {N}, \; $(\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}, \; r_i = {interac_r} \; r_e = {exclusion_r}$', fontsize=9, color='xkcd:dark grey blue')
    fig.tight_layout()
    fig.savefig(f'compare_push_no_push_fs_N_{N}_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}.png')
    plt.close(fig)

# Figure: (x-lambda, y-sdfs) for push / no push
def plotSimResults_xl_ysdfs(dfp,dfnp):
    fig, ax = plt.subplots(1,3,figsize=(9,5))
    # push
    ax[0].plot(dfp['lambda'], dfp['sdf0'], label='push', color=colors[0])
    ax[1].plot(dfp['lambda'], dfp['sdf1'], color=colors[0])
    ax[2].plot(dfp['lambda'], dfp['sdf2'], color=colors[0])
    # no push
    ax[0].plot(dfnp['lambda'], dfnp['sdf0'], label='no push', color=colors[1])
    ax[1].plot(dfnp['lambda'], dfnp['sdf1'], color=colors[1])
    ax[2].plot(dfnp['lambda'], dfnp['sdf2'], color=colors[1])
    ax[1].set_xlabel(r'$\lambda$')
    ax[0].set_ylabel(r'$\sigma \; f_0$')
    ax[1].set_ylabel(r'$\sigma \; f_1$')
    ax[2].set_ylabel(r'$\sigma \; f_2$')
    ax[0].legend()
    fig.text(0.05, 0.98, rf'$N = {N}, \; (\pi_1, \pi_2) = ({pis[0]}, {pis[1]}), \; (q_1, q_2) = ({qs[0]}, {qs[1]}), \; r_a = {arena_r}, \; r_i = {interac_r} \; r_e = {exclusion_r}$', fontsize=9, color='xkcd:dark grey blue')
    fig.tight_layout()
    fig.savefig(f'compare_push_no_push_sdfs_N_{N}_pi1_{pis[0]}_pi2_{pis[1]}_q1_{qs[0]}_q2_{qs[1]}_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}.png')
    plt.close(fig)

# ----------------------------------------- GRAPH PROPERTIES ----------------------------------------------------
def getComSizes_push_nopush():
    components_sizes_push = getCommunitySizes(N, exclusion_r, interac_r, arena_r, push=True)
    components_sizes_nopush = getCommunitySizes(N, exclusion_r, interac_r, arena_r, push=False)
    return components_sizes_push, components_sizes_nopush
    

    
# mean cluster size si comsizes es una llista de llistes, cada subllista corresponent a cada configuració
#def computeMeanClusterSize_v2(comsizes, MCSversion=0, push=True):
#    for subl in comsizes:
    

# BOX PLOT COMPARISON OF THE COMUNITY SIZES FOR push vs nopush
def boxPlotComSizes_push_nopush(components_sizes_push, components_sizes_nopush):
    fig, ax = plt.subplots()
    com_sizes_list = [components_sizes_nopush, components_sizes_push]
    ax.boxplot(com_sizes_list, labels=['no push', 'push'], showmeans=True)
    ax.set_ylabel('Community sizes')
    # ------- jitter data points -------
    xs = []
    for i in range(len(com_sizes_list)):
        xs.append(np.random.normal(i + 1, 0.08, len(com_sizes_list[i])))
    colors_rev = list(reversed(colors))
    for x, val, c in zip(xs, com_sizes_list, colors_rev):
        ax.scatter(x, val, color=c, alpha=0.1)
    # ----------------------------------
    fig.text(0.1,0.97, f'$r_a = {arena_r}$ $r_i = {interac_r}$ $N = {N}$', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'compare_push_no_push_community_sizes_N_{N}_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}.png')
    plt.close(fig)
    # i en forma d'histograma...
    # fig, ax = plt.subplots()
    # ax.hist(components_sizes_push, bins=N, color=colors[0], alpha=0.6)
    # ax.hist(components_sizes_nopush, bins=N, color=colors[1], alpha=0.6)
    # plt.show()
    # plt.close(fig)

# AVERAGE BOT DEGREE
def boxPlotBotDegree_push_nopush(components_sizes_push, components_sizes_nopush):
    degrees_push = getBotDegrees(N, exclusion_r, interac_r, arena_r, push=True)
    degrees_nopush = getBotDegrees(N, exclusion_r, interac_r, arena_r, push=False)
    fig, ax = plt.subplots()
    degrees_list = [degrees_nopush, degrees_push]
    ax.boxplot(degrees_list, labels=['no push', 'push'], showmeans=True)
    ax.set_ylabel('Degrees')
    fig.text(0.1,0.97, f'$r_a = {arena_r}$ $r_i = {interac_r}$ $N = {N}$', fontsize=9)
    # ------- jitter data points -------
    xs = []
    for i in range(len(degrees_list)):
        xs.append(np.random.normal(i + 1, 0.08, len(degrees_list[i])))
    colors_rev = list(reversed(colors))
    for x, val, c in zip(xs, degrees_list, colors_rev):
        ax.scatter(x, val, color=c, alpha=0.1)
    # ----------------------------------
    fig.tight_layout()
    fig.savefig(f'compare_push_no_push_degrees_N_{N}_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}.png')
    plt.close(fig)
    
def probComSizes(com_sizes):
    '''
    returns a dataframe with columns: 'coms' (community size), 'prob' (probability of finding that com size)
    '''
    com_sizes_counter = Counter(com_sizes)
    #coms, counts = [], []
    #for k,v in com_sizes_counter.items():
    #    coms.append(k)
    #    counts.append(v)
    coms = list(com_sizes_counter.keys())
    counts = list(com_sizes_counter.values())
    com_probs_df = pd.DataFrame({'coms':coms, 'prob':counts})
    com_probs_df.sort_values(by='coms', ignore_index=True,  inplace=True)
    com_probs_df['prob'] = com_probs_df['prob']/len(com_sizes)
    return com_probs_df
    
# power law fit to the com size distribution
def powerlawfit(x,a,k):
    return a*x**(-k)
    
def plotProbComSizes_dif_ir_push_nopush(irs, push=True, nopush=True, dofit=False, irsMaxIndexFit=None):
    '''
    irs must be a list with diferent interaction radius
    he de reprogramar aquesta funcio
    '''
    fig, ax = plt.subplots()
    figname = f'prob_com_size_N_{N}_ar_{arena_r}_er_{exclusion_r}_dif_ir'
    linestyles = ['-', '-.'] # push, nopush
    colors = plt.cm.gist_rainbow(linspace(0,1,len(irs)))
    #colors = ['xkcd:blue', 'xkcd:red']
    if push:
        figname += '_push'
        for i,ir in enumerate(irs):
            com_sizes_push = getCommunitySizes(N, exclusion_r, ir, arena_r, push=True)
            df_prob_com_sizes_push = probComSizes(com_sizes_push)
            ax.plot(df_prob_com_sizes_push['coms'], df_prob_com_sizes_push['prob'], color=colors[i], ls='None', marker='.', label=rf'${ir}$', markersize=4)
            if(dofit):
                # maxindex = 9 # a ull, hauria d'automaitzar
                maxIndex = irsMaxIndexFit[i]
                paramfit, covfit = curve_fit(powerlawfit, df_prob_com_sizes_push['coms'][0:maxIndex], df_prob_com_sizes_push['prob'][0:maxIndex])
                fit = powerlawfit(df_prob_com_sizes_push['coms'][0:maxIndex], *paramfit)
                ax.plot(df_prob_com_sizes_push['coms'][0:maxIndex], fit, ls='--', lw=0.7, alpha=0.7, color=colors[i])
                fig.text(0.15,0.4-i/10,f"$r_i = {ir}$, {round(paramfit[0],5)} · s^ - {round(paramfit[1],5)}", color=colors[i])
    if nopush:
        figname += '_nopush'
        for i,ir in enumerate(irs):
            com_sizes_nopush = getCommunitySizes(N, exclusion_r, ir, arena_r, push=False)
            df_prob_com_sizes_nopush = probComSizes(com_sizes_nopush)
            ax.plot(df_prob_com_sizes_nopush['coms'], df_prob_com_sizes_nopush['prob'], colors[i], ls='None', marker='x')
    if dofit:
        figname += '_fit'
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'Community size, $s$')
    ax.set_ylabel(r'$P(s)$')
    ax.legend(title='$r_i$', loc=[0.65,0.65])
    fig.tight_layout()
    fig.savefig(f'{figname}.png')
    plt.close(fig)

  
def plotMeanClusterSize(irs, push=True, nopush=True, MCSversion=0):
    figname = f'mean_cluster_size_ar_{arena_r}_er_{exclusion_r}_N_{N}_v{MCSversion}'
    if push: figname += '_push'
    if nopush: figname += '_nopush'
    figname += '.png'
    if push: mcs_push_df = getMeanClusterSize(irs, exclusion_r, arena_r, N, True, MCSversion)
    if nopush: mcs_nopush_df = getMeanClusterSize(irs, exclusion_r, arena_r, N, False, MCSversion)
    fig, ax = plt.subplots()
    mcs_push_df['phi'] = N*(mcs_push_df['interac_r']/arena_r)**2
    mcs_nopush_df['phi'] = N*(mcs_nopush_df['interac_r']/arena_r)**2
    ax.plot(mcs_push_df['interac_r'], mcs_push_df['mcs'], color=colors[0], label='push')
    ax.plot(mcs_nopush_df['interac_r'], mcs_nopush_df['mcs'], color=colors[1], label='nopush')
    ax.set_xlabel(r'$r_i$')
    # ax.plot(mcs_push_df['phi'], mcs_push_df['mcs'], color=colors[0], label='push')
    # ax.plot(mcs_nopush_df['phi'], mcs_nopush_df['mcs'], color=colors[1], label='nopush')
    # ax.set_xlabel(r'$\phi$')
    ax.set_ylabel(r'$\langle s \rangle$')
    fig.legend(loc=[0.15,0.8])
    fig.text(0.10, 0.97, rf'$ r_a = {arena_r}, \; r_e = {exclusion_r}, \; N = {N}$', fontsize=9)
    fig.text(0.75,0.5, r'$\langle s \rangle = \frac{\sum s^{2} n(s)}{\sum s n(s)}$', fontsize=12)
    fig.tight_layout()
    fig.savefig(figname)
    plt.close(fig)

   
   
def getAvgComponentsSize(irs):
    configType, irsdf, avgCom = [], [], []
    for ir in irs:
        avgComNoPush = np.mean(getCommunitySizes(N, exclusion_r, ir, arena_r, push=False))
        avgComPush = np.mean(getCommunitySizes(N, exclusion_r, ir, arena_r, push=True))
        configType.append('nopush'), irsdf.append(ir), avgCom.append(avgComNoPush)
        configType.append('push'), irsdf.append(ir), avgCom.append(avgComPush)
    ars = [arena_r]*len(configType)
    ers = [exclusion_r]*len(configType)
    Ns = [N] * len(configType)
    df_out = pd.DataFrame({'configType':configType, 'N':Ns, 'arena_r':ars, 'interac_r':irsdf, 'exclusion_r':ers, 'avgCom':avgCom})
    of_name = 'avgComponents.csv'
    if(os.path.exists(of_name)):
        df_old = pd.read_csv(of_name)
        for index,row in df_out.iterrows():
            bool_series = (df_old['configType']==row['configType']) & (df_old['N']==row['N']) & (df_old['arena_r']==row['arena_r']) & (df_old['interac_r']==row['interac_r']) & (df_old['exclusion_r']==row['exclusion_r'])
            if not(df_old.loc[bool_series].empty):
                df_old.drop(df_old.loc[bool_series].index,inplace=True)
        # append the new results to the csv dataframe
        df_old = pd.concat([df_old,df_out],ignore_index=True)
    else:
        df_old = df_out
    df_old = df_old.sort_values(by=['N','arena_r','interac_r','exclusion_r'], ignore_index=True)
    df_old.to_csv(of_name, index=False)
    
        
def getAvgMaxComponentSize(irs):
    configType, irsdf, avgMaxCom = [], [], []
    for ir in irs:
        avgMaxComNoPush = getAvgMaxComSize(N, exclusion_r, ir, arena_r, push=False)
        avgMaxComPush = getAvgMaxComSize(N, exclusion_r, ir, arena_r, push=True)
        configType.append('nopush'), irsdf.append(ir), avgMaxCom.append(avgMaxComNoPush)
        configType.append('push'), irsdf.append(ir), avgMaxCom.append(avgMaxComPush)
    ars = [arena_r]*len(configType)
    ers = [exclusion_r]*len(configType)
    Ns = [N] * len(configType)
    df_out = pd.DataFrame({'configType':configType, 'N':Ns, 'arena_r':ars, 'interac_r':irsdf, 'exclusion_r':ers, 'avgMaxCom':avgMaxCom})
    of_name = 'avgMaxComponents.csv'
    if(os.path.exists(of_name)):
        df_old = pd.read_csv(of_name)
        for index,row in df_out.iterrows():
            bool_series = (df_old['configType']==row['configType']) & (df_old['N']==row['N']) & (df_old['arena_r']==row['arena_r']) & (df_old['interac_r']==row['interac_r']) & (df_old['exclusion_r']==row['exclusion_r'])
            if not(df_old.loc[bool_series].empty):
                df_old.drop(df_old.loc[bool_series].index,inplace=True)
        # append the new results to the csv dataframe
        df_old = pd.concat([df_old,df_out],ignore_index=True)
    else:
        df_old = df_out
    df_old = df_old.sort_values(by=['N','arena_r','interac_r','exclusion_r'], ignore_index=True)
    df_old.to_csv(of_name, index=False)



# ----------------------------------------- GRAHP POSITIONS PROPERITES (no matter links) s-----------------------------------------------
# Average number of bots inside radius R0, std(N0) vs N0 for N = smth
def getBotRadialDistr_push_nopush(Nnormalized=False):
    radiiPush, radialDistPush, varRadialDistPush = getBotRadialDistribution(N,exclusion_r, push=True)
    radiiNoPush, radialDistNoPush, varRadialDistNoPush = getBotRadialDistribution(N,exclusion_r, push=False)
    if(Nnormalized):
        radialDistPush, radialDistNoPush = radialDistPush/N, radialDistNoPush/N
        varRadialDistPush, varRadialDistNoPush = varRadialDistPush/N**2, varRadialDistNoPush/N**2
        # stdRadialDistPush, stdRadialDistNoPush = np.sqrt(varRadialDistPush)/N, np.sqrt(varRadialDistNoPush)/N
    # stdRadialDistPush, stdRadialDistNoPush = np.sqrt(varRadialDistPush), np.sqrt(varRadialDistNoPush)
    # stdRadialDistPush, stdRadialDistNoPush = gaussian_filter1d(stdRadialDistPush, sigma=1), gaussian_filter1d(stdRadialDistNoPush, sigma=1)
    pushDistr = [radiiPush, radialDistPush, varRadialDistPush]
    nopushDistr = [radiiNoPush, radialDistNoPush, varRadialDistNoPush]
    return pushDistr, nopushDistr

# plots:

# (x-radi0, y-N0)
def plotRadialDist_xr0_yN0(pushDistr, nopushDistr):
    # unpack distributions
    radiiPush, radialDistPush, varRadialDistPush = pushDistr
    radiiNoPush, radialDistNoPush, varRadialDistNoPush = nopushDistr
    fig, ax = plt.subplots()
    ax.set_xlabel('$r_0$')
    ax.set_ylabel(r'$\langle N_0 \rangle$')
    fig.text(0.1,0.97, f'$r_a = {arena_r}$ $N = {N}$', fontsize=9)
    ax.plot(radiiPush, radialDistPush, label='push', ls='None', marker='.', color=colors[0], alpha=1.0)
    ax.plot(radiiPush, radialDistNoPush, label='no push', ls='None', marker='x', color=colors[1], alpha=1.0)
    #ax.set_xscale('log')
    #ax.set_yscale('log')
    # teorica:
    radiiTeo = np.array([1.0+i for i in range(20)], dtype='f')
    avgteoric = avgN0teo(radiiTeo, N, arena_r, exclusion_r)
    ax.plot(radiiTeo, avgteoric, ls='-', color='k', lw='0.9', label=rf'${N}r^{2}/({arena_r} - {exclusion_r})^{2})$', alpha=0.8)
    avgteoricbad = [N*r**2/arena_r**2 for r in radiiTeo]
    ax.plot(radiiTeo, avgteoricbad, ls='--', color='r', lw='0.9', label=rf'${N}r^{2}/{arena_r}^{2}$', alpha=0.8)
    fig.legend(loc='upper left')
    fig.tight_layout()
    fig.savefig(f'compare_push_no_push_radial_Ncount_N_{N}_ar_{arena_r}_er_{exclusion_r}.png')
    plt.close(fig)

# (x-N0, y-std N0)
def expocurvefit(x, a, b):
    y = a*x**b
    return y
    
def avgN0teo(r, N, arena_r, exclusion_r):
    #return N*(r/arena_r)**2 ## i) opcio basica
    return N*(r/(arena_r-exclusion_r))**2 ## ii) restant r_e a R al denominador
    #return N*r**2/((arena_r-exclusion_r)**2-N*exclusion_r**2/2) ## iii) 
    #return N*r**2*(1-N*exclusion_r**2/(1*(arena_r-exclusion_r)**2))/((arena_r-exclusion_r)**2-N*exclusion_r**2/2) ## iv)
    #return N*(r-exclusion_r)**2/(arena_r-exclusion_r)**2
    
    #return N*(r**2-N/2*exclusion_r**2)/(arena_r**2-N/2*exclusion_r**2) # "segon"
    #return N*r**2*(1-N/2*(exclusion_r/arena_r)**2)/(arena_r**2-N/2*exclusion_r**2) # "tercer"
    
def varN0teo(r, N, arena_r, exclusion_r):
    #return N*(r/arena_r)**2*(1-(r/arena_r)**2) ## i) opcio basica
    return N*(r/(arena_r-exclusion_r))**2*(1-(r/(arena_r-exclusion_r))**2) ## ii) restant r_e a R al denominador
    #return N*r**2/((arena_r-exclusion_r)**2-N*exclusion_r**2/2)*(1-r**2/((arena_r-exclusion_r)**2-N/2*exclusion_r**2)) ## iii)
    #return N*r**2*(1-N*exclusion_r**2/(1*(arena_r-exclusion_r)**2))/((arena_r-exclusion_r)**2-N*exclusion_r**2/2)*(1-r**2*(1-N*exclusion_r**2/(1*(arena_r-exclusion_r)**2))/((arena_r-exclusion_r)**2-N/2*exclusion_r**2)) ## iv)
    #p = ((r-exclusion_r)**2-avgN0teo(r,N,arena_r,exclusion_r)*exclusion_r/(2*N))/((arena_r-exclusion_r)**2-N*exclusion_r**2/2)
    #q = (arena_r-exclusion_r)**2 - (r-exclusion_r)**2 - exclusion_r**2*(N-avgN0teo(r,N,arena_r,exclusion_r)/N)/2
    #q /= (arena_r-exclusion_r)**2 - N/2*exclusion_r**2
    #return N*p*q
    
    # return N*(r**2-N/2*exclusion_r**2)/(arena_r**2-N/2*exclusion_r**2)*(1-(r**2-N/2*exclusion_r**2)/(arena_r**2-N/2*exclusion_r**2)) # segon
    # return N*r**2*(1-N/2*(exclusion_r/arena_r)**2)/(arena_r**2-N/2*exclusion_r**2)*(1-r**2*(1-N/2*(exclusion_r/arena_r)**2)/(arena_r**2-N/2*exclusion_r**2)) # tercer
    

def plotRadialDist_xN0_yFlucN0(pushDistr, nopushDistr, Nnorm = False, saveDataToFile = False):
    # unpack distributions
    radiiPush, radialDistPush, varRadialDistPush = pushDistr
    radiiNoPush, radialDistNoPush, varRadialDistNoPush = nopushDistr
    # compute standar deviations:
    stdRadialDistPush, stdRadialDistNoPush = np.sqrt(varRadialDistPush), np.sqrt(varRadialDistNoPush)
    # N normalization:
    if Nnorm:
        radialDistPush /= N
        stdRadialDistPush /= N
        radialDistNoPush /= N
        stdRadialDistNoPush /= N
    fig, ax = plt.subplots()
    ax.set_xlabel(r'$\langle N_0 \rangle$')
    ax.set_ylabel(r'$\sigma (N_0)$')
    fig.text(0.1, 0.97, f'$r_a = {arena_r}$ $r_e = {exclusion_r}$ $N = {N}$', fontsize=9)
    ax.plot(radialDistPush, stdRadialDistPush, label='push', color=colors[0], marker='.', ls='None')
    ax.plot(radialDistNoPush, stdRadialDistNoPush, label='no push', color=colors[1], marker='x', ls='None')
    if saveDataToFile:
        df = pd.DataFrame({'n':radialDistPush, 'stdn':stdRadialDistPush})
        df.to_csv(f'bots_distr_xN_ySTDN_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}_push.csv', index=False)
        df = pd.DataFrame({'n':radialDistNoPush, 'stdn':stdRadialDistNoPush})
        df.to_csv(f'bots_distr_xN_ySTDN_ar_{arena_r}_ir_{interac_r}_er_{exclusion_r}_nopush.csv', index=False)
    # ------- fit the points to find the exponent -----------
    indexFit = 11
    paramPush, covPush = curve_fit(expocurvefit, radialDistPush[0:indexFit], stdRadialDistPush[0:indexFit])
    paramNoPush, covNoPush = curve_fit(expocurvefit, radialDistNoPush[0:indexFit], stdRadialDistNoPush[0:indexFit])
    fitPush = expocurvefit(radialDistPush[0:indexFit], *paramPush)
    fitNoPush = expocurvefit(radialDistNoPush[0:indexFit], *paramNoPush)
    ax.plot(radialDistPush[0:indexFit], fitPush, color=colors[0], ls='--', lw='0.7')
    ax.plot(radialDistNoPush[0:indexFit], fitNoPush, color=colors[1], ls='--', lw='0.7')
    # ax.plot(radialDistPush[0:indexFit], np.sqrt(radialDistPush)[0:indexFit], ls='--', color='k', lw='0.8')
    # ---------------- linea teorica ----------------
    radiiTeo = np.array([1.5+i for i in range(18)], dtype='f')
    avgteoric = avgN0teo(radiiTeo, N, arena_r, exclusion_r)
    varteoric = varN0teo(radiiTeo, N, arena_r, exclusion_r)
    stdteoric = np.sqrt(varteoric)
    if Nnorm:
        avgteoric /= N
        stdteoric /= N
    ax.plot(avgteoric, stdteoric, ls=':', color='k', lw='0.8')
    fig.text(0.45, 0.55, f'push: {paramPush[0]:.4f} · N0^{paramPush[1]:.4f}', color=colors[0])
    fig.text(0.45, 0.50, f'no push: {paramNoPush[0]:.4f} · N0^{paramNoPush[1]:.4f}', color=colors[1])
    #fig.text(0.45, 0.45, r'$p=\frac{r^{2}}{(R-r_e)^{2}}$') # ii)
    #fig.text(0.45, 0.45, r'$p=\frac{r^{2}}{(R-r_e)^{2}-\frac{N}{2}r_e^{2}}$') # iii)
    #fig.text(0.45, 0.45, r'$p=\frac{r^{2}\left(1-\frac{N r_e^{2}}{2(R-r_e)^{2}}\right)}{(R-r_e)^{2}-\frac{N}{2}r_e^{2}}$') # iv)
    # ---- savefig ----
    fig.tight_layout()
    fig.savefig(f'compare_push_no_push_stdN0_vs_N0_N_{N}_ar_{arena_r}_er_{exclusion_r}.png')


def main():
    # sim results ----------------
    # dfp, dfnp = getSimResDf()
    # plotSimResults_xl_yfs(dfp,dfnp)
    # plotSimResults_xl_ysdfs(dfp,dfnp)
    # ------------------------------
    # graph properties -------------
    # components_sizes_push, components_sizes_nopush = getComSizes_push_nopush()
    # boxPlotComSizes_push_nopush(components_sizes_push, components_sizes_nopush)
    # boxPlotBotDegree_push_nopush(components_sizes_push, components_sizes_nopush)
    #plotProbComSizes_dif_ir_push_nopush([4.0, 7.0, 7.5], nopush=False, dofit=True, irsMaxIndexFit=[19, 9, 9])
    irs = [4.0, 4.5, 4.8, 4.9, 5.0, 5.1, 5.3, 5.5, 6.0, 6.5, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.5, 8.0, 9.0, 10.0]
    # Per N=492:
    # irs = [4.0, 5.0, 5.5, 6.0, 6.5, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.5, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 10.0, 10.5, 11.0]
    plotMeanClusterSize(irs, MCSversion = 3)
    # getAvgMaxComponentSize([4.0, 5.0, 6.0, 7.0, 8.0])
    # getAvgComponentsSize([4.0, 5.0, 6.0, 7.0, 8.0])
    # ------------------------------
    # position distribution properties ---------------
    # pushDistr, nopushDistr = getBotRadialDistr_push_nopush()
    # plotRadialDist_xr0_yN0(pushDistr, nopushDistr)
    # plotRadialDist_xN0_yFlucN0(pushDistr, nopushDistr, saveDataToFile = True) # , Nnorm=True

if __name__ == '__main__':
    main()
