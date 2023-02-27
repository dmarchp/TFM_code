from cProfile import label
import pandas as pd
import numpy as np
import glob
import os
import subprocess
import matplotlib.pyplot as plt
import igraph as ig
from scipy.ndimage import gaussian_filter1d
from collections import Counter
from graph_properties_functions import *

arena_r = 20.0

# Plot the evolution of N0 as a function of r0 for fixed N and some exclusion radius
# N = 35
# fig,ax = plt.subplots()
# exclusion_r = [0.0, 1.5]
# for er in exclusion_r:
#     radii, radialDist, varRadialDist = getBotRadialDistribution(N,er)
#     ax.plot(radii, radialDist, label=f'{er}')
#     ax.fill_between(radii, radialDist-np.sqrt(varRadialDist), radialDist+np.sqrt(varRadialDist), alpha=0.2)
#     # theoretical line
#     rho = N/(np.pi*(arena_r-er)**2)
#     ax.plot(radii, rho*np.pi*np.array(radii)**2, color='k', ls='--', alpha=0.5)
# ax.legend(title=r'$r_e$')
# ax.set_xlabel('$r_0$ (cm)')
# ax.set_ylabel('Number of bots inside $r_0$')
# fig.text(0.1,0.97, f'$r_a = {arena_r}$', fontsize=9)
# fig.text(0.3,0.6, r'dashed = $\frac{r_0^2}{(R-r_e)^2}$', fontsize=12)
# fig.tight_layout()
# fig.savefig(f'radial_Ncount_N_{N}_ar_{arena_r}_many_er.png')
# plt.close(fig)

# save data from the last figure (if necessary):
# N = 35
# exclusion_r = [0.0, 1.5]
# for er in exclusion_r:
#     radii, radialDist, varRadialDist = getBotRadialDistribution(N,er)
#     std = np.sqrt(varRadialDist)
#     df = pd.DataFrame({'radius':radii, 'N':radialDist, 'varN':varRadialDist, 'stdN':std})
#     df.to_csv(f'bots_concentric_radial_dist_N_{N}_ar_{arena_r}_er_{er}.csv', index=False)


# # Plot the evolution of N0 as a function of r0 for fixed exclusion radius and some N
# Ns = [25, 30, 35, 40, 50, 60, 70, 80]
# colors = plt.cm.gist_rainbow(np.linspace(0,1,len(Ns)))
# exclusion_r = 1.5
# half_arena = arena_r/np.sqrt(2) # half of the area achieved at R/sqrt(2)
# half_ef_arena = (arena_r-exclusion_r)/np.sqrt(2)
# fig,ax = plt.subplots()
# fig2,ax2 = plt.subplots()
# for i,N in enumerate(Ns):
#     radii, radialDist, varRadialDist = getBotRadialDistribution(N,exclusion_r)
#     radialDist = radialDist/N
#     stdRadialDist = np.sqrt(varRadialDist)
#     stdRadialDist = stdRadialDist/N
#     stdRadialDist_filtered = gaussian_filter1d(stdRadialDist, sigma=1)
#     # varRadialDist = varRadialDist/N**2
#     # varRadialDist_filtered = gaussian_filter1d(varRadialDist, sigma=1)
#     ax.plot(radii, radialDist, label=f'{N}', color=colors[i])
#     ax2.plot(radii, stdRadialDist_filtered, label=f'{N}', color=colors[i])
#     # ax2.plot(radii, varRadialDist_filtered, label=f'{N}', color=colors[i])
# for a in [ax,ax2]:
#     a.axvline(half_arena, color='xkcd:light grey', ls='--')
#     a.axvline(half_ef_arena, color='xkcd:light grey', ls='--')
#     a.legend(title='N')
#     a.set_xlabel('$r_0$ (cm)')
# ax.axhline(0.5, color='xkcd:light grey', ls='--')
# ax.set_ylabel('$N_0/N$')
# # ax2.set_ylabel('$Var(N_0)$')
# ax2.set_ylabel('$std(N_0)/N$')
# fig.text(0.1,0.97, f'$r_a = {arena_r}$ $r_e = {exclusion_r}$', fontsize=9)
# fig.tight_layout()
# fig.savefig(f'radial_Ncount_ar_{arena_r}_er_{exclusion_r}_many_N.png')
# fig2.text(0.1,0.97, f'$r_a = {arena_r}$ $r_e = {exclusion_r}$', fontsize=9)
# fig2.tight_layout()
# fig2.savefig(f'var_radial_Ncount_ar_{arena_r}_er_{exclusion_r}_many_N.png')
# plt.close(fig)
# plt.close(fig2)

# x- N0 average, y- Var(N0)
# Ns = [25, 30, 35, 40, 50, 60, 70, 80]
# colors = plt.cm.gist_rainbow(np.linspace(0,1,len(Ns)))
# exclusion_r = 1.5
# fig,ax = plt.subplots()
# for i,N in enumerate(Ns):
#     radii, radialDist, varRadialDist = getBotRadialDistribution(N,exclusion_r,arena_r=arena_r)
#     radialDist = radialDist/N
#     stdRadialDist = np.sqrt(varRadialDist)
#     stdRadialDist = stdRadialDist/N
#     # stdRadialDist = stdRadialDist/np.sqrt(N)
#     # varRadialDist = varRadialDist/N**2
#     # varRadialDist_filtered = gaussian_filter1d(varRadialDist, sigma=1)
#     # ax.plot(radialDist, varRadialDist_filtered, label=f'{N}', color=colors[i])
#     stdRadialDist_filtered = gaussian_filter1d(stdRadialDist, sigma=1)
#     ax.plot(radialDist, stdRadialDist_filtered, label=f'{N}', color=colors[i])
#     #ax.plot(radialDist, np.sqrt(radialDist), color='k', ls='--') # N/(np.pi*arena_r**2)*   4/N*
#     #ax.plot(radialDist, 0.5*radialDist**(3/5), color='k', ls='--')
#     #j = radii.index(half_arena)
#     #ax.plot(radialDist[j], stdRadialDist_filtered[j], color=colors[i], marker='*')
# # ax.set_yscale('log')
# # ax.set_xscale('log')
# ax.legend(title='N')
# ax.set_xlabel('$N_0 / N$')
# # ax.set_ylabel('$Var(N_0) / N$')
# ax.set_ylabel('$ std(N_0) / N$')
# fig.text(0.1,0.97, f'$r_a = {arena_r}$ $r_e = {exclusion_r}$', fontsize=9)
# fig.tight_layout()
# fig.savefig(f'VarN0_vs_N0_ar_{arena_r}_er_{exclusion_r}_many_N.png')
# plt.close(fig)

# mateixa figura pero nomes una N i inset de la part de N0 mes petita
# from mpl_toolkits.axes_grid1.inset_locator import (inset_axes, InsetPosition, mark_inset)
# from scipy.optimize import curve_fit
# def expocurvefit(x, a, b):
#     y = a*x**b
#     return y
# Ns = [35, ]
# arena_r = 20.0
# colors = plt.cm.gist_rainbow(np.linspace(0,1,len(Ns)))
# exclusion_r = 1.5
# fig,ax = plt.subplots()
# #axr = ax.twiny()
# # axx = ax.twinx()
# for i,N in enumerate(Ns):
#     radii, radialDist, varRadialDist = getBotRadialDistribution(N,exclusion_r,arena_r=arena_r)
#     radialDist = radialDist #/N
#     stdRadialDist = np.sqrt(varRadialDist)
#     stdRadialDist = stdRadialDist #/N
#     #stdRadialDist_filtered = gaussian_filter1d(stdRadialDist, sigma=1)
#     ax.plot(radialDist, stdRadialDist, label=f'{N}', color=colors[i], marker='.', ls='None')
#     ax.plot(radialDist, np.sqrt(radialDist), color='k', ls='--', lw='0.7')
#     # axr.plot(radii, stdRadialDist_filtered, alpha=0.2)
#     # axx.plot(radialDist, radii)
#     # ------- ajust exponent -------
#     parameters, covariance = curve_fit(expocurvefit, radialDist[0:10], stdRadialDist[0:10])
#     fit = expocurvefit(radialDist[0:10], *parameters)
#     ax.plot(radialDist[0:10], fit, color='xkcd:indian red', ls='--', lw='0.7')
#     fig.text(0.15, 0.75, '{a:.4f} · N0^{b:.4f}'.format(a=round(parameters[0],4), b=round(parameters[1],4)))
#     # ----------- inset ------------
#     # ax2 = plt.axes([0,0,1,1])
#     # ip = InsetPosition(ax, [0.55,0.55,0.42,0.42])
#     # ax2.set_axes_locator(ip)
#     # mark_inset()
#     # mark_inset(ax, ax2, loc1=2, loc2=4, fc="none", ec='xkcd:light grey')
#     # ax2.plot(radialDist[0:10], stdRadialDist_filtered[0:10], color=colors[i])
#     # ax2.plot(radialDist[0:10], np.sqrt(radialDist)[0:10], color='k', ls='--')
#     # ax2.set_yscale('log')
#     # ax2.set_xscale('log')
# # --------- prova vlines ---------------
# indexs = [4,9,14]
# for i in indexs:
#     ax.axvline(radialDist[i], label=rf'$r_0 = {radii[i]}$', color='xkcd:light gray', ls='--', lw='0.7')
# #axr.axvline(14.14, label=r'$r_0^{N/2}$', color='xkcd:tan', ls='--')
# # axx.axhline((arena_r-exclusion_r)/np.sqrt(2), color='xkcd:tan', ls='--', xmin=0.25, xmax=1.0)
# # ax.axvline(Ns[0]/2, color='xkcd:tan', ls='--')
# # --------------------------------------
# ax.legend(title='N')
# ax.set_xlabel(r'$\langle N_0 \rangle$')
# # axr.set_xlabel(r'$r_0$')
# ax.set_ylabel('$ \sigma(N_0)$')
# fig.text(0.15, 0.65, r'$ \sigma(N_0) \simeq \langle N_0 \rangle^{0.5}$')
# fig.text(0.1,0.97, f'$r_a = {arena_r}$ $r_e = {exclusion_r}$', fontsize=9)
# fig.tight_layout()
# fig.savefig(f'stdN0_vs_N0_ar_{arena_r}_er_{exclusion_r}_many_N_inset.png') # , bbox_inches='tight', pad_inches=0.01
# plt.close(fig)



# SIZE OF THE GRAPH COMPONENTS
# Ns = [20, 25, 30, 35, 40, 50, 60, 70, 80]
# exclusion_r = 1.5
# interac_r = 7.0
# max_sizes = []
# avg_sizes = []
# sizes_lists = []
# std_sizes = []
# for i,N in enumerate(Ns):
#     com_sizes = getCommunitySizes(N, exclusion_r, interac_r)
#     sizes_lists.append(com_sizes)
#     max_sizes.append(max(com_sizes))
#     avg_sizes.append(np.array(com_sizes).mean())
#     std_sizes.append(np.array(com_sizes).std())
# fig, ax = plt.subplots(1,2)
# avg_sizes = np.array(avg_sizes)
# std_sizes = np.array(std_sizes)
# ax[0].plot(Ns, max_sizes)
# ax[0].grid(axis='both', color='xkcd:light grey', ls='--')
# ax[1].grid(axis='both', color='xkcd:light grey', ls='--')
# # Normalize sizes list to the size of the system:
# sizes_lists_norm= [np.array(sizes)/N for sizes,N in zip(sizes_lists,Ns)]
# ax[1].boxplot(sizes_lists_norm, labels=Ns)
# ax[0].set_xlabel('N')
# ax[1].set_xlabel('N')
# ax[0].set_title('Max Components Size')
# ax[1].set_title('Avg Component Size')
# fig.tight_layout()
# fig.savefig(f'components_ar_{arena_r}_er_{exclusion_r}_many_N.png')


# BOX PLOT COMPARISON OF THE COMUNITY SIZES FOR DIFFERENT r_e
N = 35
ers = [0.0, 1.5]
interac_r = 5.0
com_sizes_list = []
for er in ers:
    com_sizes = getCommunitySizes(N, er, interac_r)
    com_sizes_list.append(com_sizes)
fig, ax = plt.subplots()
ax.boxplot(com_sizes_list, labels=ers, showmeans=True)
ax.set_xlabel('$r_e$')
ax.set_ylabel('Community sizes')
fig.text(0.1,0.97, f'$r_a = {arena_r}$ $r_i = {interac_r}$ $N = {N}$', fontsize=9)
fig.tight_layout()
fig.savefig(f'community_sizes_difr_er_N_{N}_ar_{arena_r}_ir_{interac_r}.png')
# save data to file:
df0 = pd.DataFrame({'er_0.0':com_sizes_list[0]})
df0['er_0.0'] = df0['er_0.0'].astype('int16')
df1 = pd.DataFrame({'er_1.5':com_sizes_list[1]})
df1['er_1.5'] = df1['er_1.5'].astype('int16')
df = pd.concat([df0, df1], axis=1)
df.to_csv(f'comSizes_diff_er_N_{N}_ar_{arena_r}_ir_{interac_r}.csv', index=False)

# PROBABILITY OF COMUNITY SIZE FOR DIFFERENT r_e
# N = 35
# ers = [0.0, 0.7, 1.1, 1.5]
# interac_r = 7.0
# fig, ax = plt.subplots()
# for er in ers:
#     com_sizes = getCommunitySizes(N, er, interac_r)
#     com_sizes_counter = Counter(com_sizes)
#     coms, counts = [], []
#     for k,v in com_sizes_counter.items():
#         coms.append(k)
#         counts.append(v)
#     com_probs_df = pd.DataFrame({'coms':coms, 'prob':counts})
#     com_probs_df.sort_values(by='coms', ignore_index=True,  inplace=True)
#     com_probs_df['prob'] = com_probs_df['prob']/len(com_sizes)
#     com_probs_df['prob'] = gaussian_filter1d(com_probs_df['prob'], sigma=1)
#     ax.plot(com_probs_df['coms'], com_probs_df['prob'], label=rf'${er}$')
# ax.set_xlabel(r'Community size, $s$')
# ax.set_ylabel(r'$P(s)$')
# ax.legend(title='$r_e$')
# fig.tight_layout()
# fig.savefig(f'prob_com_size_N_{N}_ar_{arena_r}_ir_{interac_r}_dif_er.png')

# PROBABILITY OF COMUNITY SIZE FOR DIFFERENT r_i
# N = 35
# irs = [4.0, 5.0, 6.0, 7.0]
# exclusion_r = 1.5
# fig, ax = plt.subplots()
# for ir in irs:
#     com_sizes = getCommunitySizes(N, exclusion_r, ir)
#     com_sizes_counter = Counter(com_sizes)
#     coms, counts = [], []
#     for k,v in com_sizes_counter.items():
#         coms.append(k)
#         counts.append(v)
#     com_probs_df = pd.DataFrame({'coms':coms, 'prob':counts})
#     com_probs_df.sort_values(by='coms', ignore_index=True,  inplace=True)
#     com_probs_df['prob'] = com_probs_df['prob']/len(com_sizes)
#     com_probs_df['prob'] = gaussian_filter1d(com_probs_df['prob'], sigma=1)
#     ax.plot(com_probs_df['coms'], com_probs_df['prob'], label=rf'${ir}$')
# ax.set_xlabel(r'Community size, $s$')
# ax.set_ylabel(r'$P(s)$')
# ax.legend(title='$r_i$')
# fig.tight_layout()
# fig.savefig(f'prob_com_size_N_{N}_ar_{arena_r}_er_{exclusion_r}_dif_ir.png')

