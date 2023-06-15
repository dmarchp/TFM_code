def plot_hmap(magnitud, vmin, vmax, cmap, tline=False, adjust_cbar=False):
    df_to_map = df_phase_space.pivot('pi2','pi1',magnitud) # lambda rows, pi columns
    # read hmap:
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
    # Overwrite the vmin,vmax values if adjust_cbar is true
    if(adjust_cbar):
        zmax = abs(z).max()
        vmin = -zmax
        vmax = zmax
    # plot the map:
    fig, ax = plt.subplots(figsize=(8,6))
    im = ax.pcolormesh(xgrid, ygrid, z, cmap=cmap, vmin=vmin, vmax=vmax, shading='auto')
    fig.colorbar(im, ax=ax)
    ax.set_xlabel(r"$\pi_{1}$")
    ax.set_ylabel(r"$\pi_{2}$")
    # read and plot the theoretical line:
    if(tline):
        df_Tline = get_Tline(magnitud,df_to_map)
        if not(df_Tline.empty):
            index_from = 0
            ax.plot(list(df_Tline['pi1'])[index_from:], list(df_Tline['pi2'])[index_from:])
        if(adjust_cbar):
            plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap_wTline_adjust_cbar.png', bbox_inches='tight', pad_inches=0.01)
        else:
            plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap_wTline.png', bbox_inches='tight', pad_inches=0.01)
    else:
        if(adjust_cbar):
            plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap_adjust_cbar.png', bbox_inches='tight', pad_inches=0.01)
        else:
            plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap.png', bbox_inches='tight', pad_inches=0.01)
            


# Spline interpolation to the heatmap:
def plot_hmap_spline(magnitud, vmin, vmax, cmap, tline=False, adjust_cbar=False):
    df_to_map = df_phase_space.pivot('pi2','pi1',magnitud) # lambda rows, pi columns
    # read hmap and carry out the interpolation:
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
    tck = interpolate.bisplrep(xgrid, ygrid, z)
    xnew, ynew = np.mgrid[min(pi1):max(pi1):complex(0,(max(pi1)-min(pi1))*100+1), min(pi2):max(pi2):complex(0,(max(pi2)-min(pi2))*100+1)]
    znew = interpolate.bisplev(xnew[:,0], ynew[0,:], tck)
    # Overwrite the vmin,vmax values if adjust_cbar is true
    if(adjust_cbar):
        zmax = abs(z).max()
        vmin = -zmax
        vmax = zmax
    # plot the interpolated map:
    fig, ax = plt.subplots(figsize=(8,6))
    im = ax.pcolormesh(xnew, ynew, znew, cmap=cmap, vmin=vmin, vmax=vmax, shading='auto')
    fig.colorbar(im, ax=ax)
    ax.set_xlabel(r"$\pi_{1}$")
    ax.set_ylabel(r"$\pi_{2}$")
    # read and plot the theoretical line:
    if(tline):
        df_Tline = get_Tline(magnitud,df_to_map)
        if not(df_Tline.empty):
            #print(df_Tline)
            #index_from = list(df_Tline['pi1']).index(xnew[0][0])
            index_from = 0
            ax.plot(list(df_Tline['pi1'])[index_from:], list(df_Tline['pi2'])[index_from:])
        if(adjust_cbar):
            plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap_spline_wTline_adjust_cbar.png', bbox_inches='tight', pad_inches=0.01)
        else:
            plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap_spline_wTline.png', bbox_inches='tight', pad_inches=0.01)
    else:
        if(adjust_cbar):
            plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap_spline_adjust_cbar.png', bbox_inches='tight', pad_inches=0.01)
        else:
            plt.savefig(f'q1_{q1}_q2_{q2}_l_{lstr}_{magnitud}_hmap_spline.png', bbox_inches='tight', pad_inches=0.01)
