from graph_properties_functions import *
import matplotlib.pyplot as plt
from math import pi
from scipy.optimize import curve_fit
from numpy import linspace
from collections import Counter

exclusion_r = 1.5
#arena_r = 20.0
irsMCSGlobal = [i/10 for i in range(40,103,3)]
irsMAXcomp = [6.0, 7.0, 8.0]
#density0 = 35/(pi*20.0**2)
systems_info0 = {
35:{'arena_r':20.0, 'irsMCS':irsMCSGlobal+[6.3,6.5,6.6,6.8,6.9]},
219:{'arena_r':50.0, 'irsMCS':irsMCSGlobal+[6.2,6.3,6.5,7.2,7.4,7.5,7.7]},
492:{'arena_r':75.0, 'irsMCS':irsMCSGlobal+[6.3,6.5,6.6,6.8,6.9]},
709:{'arena_r':90.0, 'irsMCS':irsMCSGlobal+[6.2,6.3,6.5]},
965:{'arena_r':105.0, 'irsMCS':irsMCSGlobal+[6.2,6.3,6.5]}
}

# extra:
#systems_info0[1479] = {'arena_r':130.0, 'irsMCS':irsMCSGlobal}
#systems_info0[2240] = {'arena_r':160.0, 'irsMCS':irsMCSGlobal}

def mcs_different_system_size(systems_info, push=False):
    fig, ax = plt.subplots()
    for k,v in systems_info.items():
        N, arena_r, irs = k, v['arena_r'], v['irsMCS']
        irs.sort()
        dfMCS = getMeanClusterSize(irs, exclusion_r, arena_r, N, push)
        ax.plot(dfMCS['interac_r'], dfMCS['mcs'], label=f'{N}', marker='x', markersize=1.0, linewidth=1.0)
        density = N/(pi*arena_r**2)
    fig.legend(title='N')
    ax.set_xlabel('$r_i$')
    ax.set_ylabel('MCS')
    # fig.text(0.6, 0.6, f'$\\rho = {round(density,3)}$ bots/cm$^{2}$')
    fig.suptitle(f'$\\rho = {round(density,3)}$ bots/cm$^{2}$, $r_e = {exclusion_r}$, push = {push}', fontsize=9)
    fig.tight_layout()
    pushLabel = 'push' if push else 'nopush'
    fig.savefig(f'mean_cluster_size_sysSizes_er_{exclusion_r}_dens_{round(density,3)}_{pushLabel}.png')


def powerLaw(x,a,b):
    return a*x**b

def plot_avgMaxComSize_diff_sys_size(systems_info, irs, push=False, irs_fit=[]):
    first_key = next(iter(systems_info))
    density = first_key/(pi*systems_info[first_key]['arena_r']**2)
    pushLabel = 'push' if push else 'nopush'
    fig, ax  = plt.subplots()
    colors = plt.cm.gist_rainbow(linspace(0,1,len(irs)))
    for i,ir in enumerate(irs):
        dfAMC = getAvgMaxComSize_different_system_size(systems_info, ir, exclusion_r, push)
        ax.plot(dfAMC['N'], dfAMC['avg'], label=f'{ir}', marker='x', lw=0, color=colors[i])
        if ir in irs_fit:
            paramfit, covfit = curve_fit(powerLaw, dfAMC['N'], dfAMC['avg'])
            fit = powerLaw(dfAMC['N'], *paramfit)
            ax.plot(dfAMC['N'], fit, ls='--', lw=0.7, alpha=0.7, color=colors[i])
            fig.text(0.6,0.1+i*0.05, f'{round(paramfit[0],3)} N ^{round(paramfit[1],6)}', color=colors[i], fontsize=9)
    ax.set_xlabel('N')
    ax.set_ylabel('average max component')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(title='$r_i$')
    fig.suptitle(f'$\\rho = {round(density,3)}$ bots/cm$^{2}$, $r_e = {exclusion_r}$, push = {push}', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'avg_max_comp_sysSizes_er_{exclusion_r}_dens_{round(density,3)}_{pushLabel}.png')

def getAvgMaxComSize_different_system_size(systems_info, ir, exclusion_r, push):
    ...

def getAvgBotDegrees_irs(irs, N, exclusion_r, arena_r, push=False):
    avg_l, std_l = [], []
    for ir in irs:
        degrees = getBotDegrees(N, exclusion_r, ir, arena_r, push=push)
        degrees = np.array(degrees)
        avg_l.append(np.mean(degrees)), std_l.append(np.std(degrees))
    df = pd.DataFrame({'interac_r':irs, 'avg':avg_l, 'std':std_l})
    pushLabel = 'push' if push else 'nopush'
    df.to_csv(f'other_res_files/avgDegree_N_{N}_ar_{arena_r}_er_{exclusion_r}_{pushLabel}.csv', index=False)

def componentsHistogram(N, interac_r, exclusion_r, arena_r, excludeGiantComp = True, push=False):
    com_sizes = getCommunitySizes(N, exclusion_r, interac_r, arena_r, push, excludeGiantComp, exclusionVersion=0)
    fig, ax = plt.subplots()
    ax.hist(com_sizes, bins=N, range=(0,N))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(100,200)
    fig.text(0.1, 0.97, f'N = {N}, $r_a$ = {arena_r}, $r_i$ = {interac_r}, Quenched Config, GC excluded')
    fig.tight_layout()
    fig.savefig(f'com_sizes_histogram_N_{N}_ar_{arena_r}_ir_{interac_r}_quenched_zoom.png')
    plt.close(fig)
    
def plotComSizes_difN(Ns, arena_rs, interac_rs, exclusion_r, prob=False, push=False, excludeGiantComp = False, dataToFile = False):
    pushLabel = 'push' if push else 'nopush'
    gcLabel = 'excludedGC' if excludeGiantComp else ''
    fig, ax = plt.subplots()
    ylabel = 'P(s)' if prob else 'N(s)'
    ax.set(xlabel='s', ylabel=ylabel, xscale='log', yscale='log')
    for N, ar, ir in zip(Ns, arena_rs, interac_rs):
        com_sizes = getCommunitySizes(N, exclusion_r, ir, ar, push, excludeGiantComp, exclusionVersion=0)
        # fer el conteig de N(s)
        com_sizes_counter = Counter(com_sizes)
        coms = list(com_sizes_counter.keys())
        counts = list(com_sizes_counter.values())
        probs = [count/len(com_sizes) for count in list(com_sizes_counter.values())]
        # logarithmic binning:
        box_edges = np.geomspace(10, max(coms),10)
        
        #irs = [ir]*len(coms)
        com_counts_df = pd.DataFrame({'coms':coms, 'counts':counts, 'probs':probs})
        com_counts_df = com_counts_df.sort_values(by='coms', ignore_index=True)
        if dataToFile:
            filename = f'comSizesCounts_N_{N}_ar_{ar}_ir_{ir}_er_{exclusion_r}_{pushLabel}_{gcLabel}.csv'
            com_counts_df.to_csv(filename, index=False)
        # plot:
        if prob:
            ax.plot(com_counts_df['coms'], com_counts_df['probs'], label=rf'{N}, $r_i^{{*}} = {ir}$', marker='.', ls='None')
        else:
            ax.plot(com_counts_df['coms'], com_counts_df['counts'], label=rf'{N}, $r_i^{{*}} = {ir}$', marker='.', ls='None')
    fig.text(0.25, 0.97, f'$excludeGiantComp = {excludeGiantComp}, push = {push}$')
    fig.legend(title='N', loc=(0.7,0.7))
    fig.tight_layout()
    figName = 'comSizesProbs' if prob else 'comSizesCounts'
    for N in Ns:
        figName += f'_{N}'
    figName += f'_er_{exclusion_r}_{pushLabel}_{gcLabel}.png'
    fig.savefig(figName)


def main():
    ###### mcs individual sizes ######
    #getMeanClusterSize(systems_info0[35]['irsMCS'], 1.5, 20.0, 35, push=False)
    #getMeanClusterSize([6.2,6.4], 1.5, 20.0, 35, push=False)
    #getMeanClusterSize(systems_info0[492]['irsMCS'], 1.5, 75.0, 492, push=False)
    # mcs_different_system_size(systems_info0)
    # mcs_different_system_size(systems_info0, True)
    # plot_avgMaxComSize_diff_sys_size(systems_info0, [6.0, 6.5, 7.0, 7.9, 10.0], push=False, irs_fit=[6.5, 7.0])
    # plot_avgMaxComSize_diff_sys_size(systems_info0, [6.0, 6.3, 6.5, 7.0, 7.9, 10.0], irs_fit=[6.3, 7.0])
    #for N in [492,]:
    #    for ir in [3.5, 4.0, 4.5, 5.0]:
    #        a,b = getAvgMaxComSize(N, 1.5, ir, arena_r=75.0)
    #        print(f'{N},{ir},{a},{b}')
    #irs = [3.5, 3.8, 4.0, 4.5, 5.0, 5.5, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]
    # getAvgBotDegrees_irs(irs, 35, 1.5, 20.0)
    #componentsHistogram(492, 6.0, 1.5, 75.0)
    ####
    # a dia 21 de febrer 2023 ho estic fent amb 1000 configs N35, 250 configs N492
    plotComSizes_difN([35,492], [20.0, 75.0], [6.5, 6.4], 1.5, prob=True, push=False, excludeGiantComp = False, dataToFile=True)
    plotComSizes_difN([35,492], [20.0, 75.0], [6.5, 6.4], 1.5, prob=True, push=False, excludeGiantComp = True, dataToFile=True)
    

if __name__ == '__main__':
    main()
