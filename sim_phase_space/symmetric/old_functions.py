def plot_hmap(magnitud, vmin, vmax, cmap, tline=False, adjust_cbar=False):
    df_to_map = df_phase_space.pivot('lambda','pi',magnitud) # lambda rows, pi columns
    # read hmap:
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
    if(adjust_cbar):
        zmax = abs(z).max()
        vmin = -zmax
        vmax = zmax
    fig, ax = plt.subplots()
    im = ax.pcolormesh(xgrid, ygrid, z, cmap=cmap, vmin=vmin, vmax=vmax, shading='auto')
    fig.colorbar(im, ax=ax)
    ax.set_xlabel(r"$\pi_{1,2}$")
    ax.set_ylabel(r"$\lambda$")
    # read and plot the theoretical line:
    if(tline):
        df_Tline = get_Tline(magnitud,df_to_map)
        if not(df_Tline.empty):
            index_from = list(df_Tline['pi']).index(xnew[0][0])
            ax.plot(list(df_Tline['pi'])[index_from:], list(df_Tline['lambda'])[index_from:])
        if(adjust_cbar):
            plt.savefig(f'q1_{q1}_q2_{q2}_{magnitud}_hmap_wTline_adjust_cbar.png', bbox_inches='tight', pad_inches=0.01)
        else:
            plt.savefig(f'q1_{q1}_q2_{q2}_{magnitud}_hmap_wTline.png', bbox_inches='tight', pad_inches=0.01)
    else:
        if(adjust_cbar):
            plt.savefig(f'q1_{q1}_q2_{q2}_{magnitud}_hmap_adjust_cbar.png', bbox_inches='tight', pad_inches=0.01)
        else:
            plt.savefig(f'q1_{q1}_q2_{q2}_{magnitud}_hmap.png', bbox_inches='tight', pad_inches=0.01)
        
# Spline interpolation to the heatmap:
def plot_hmap_spline(magnitud, vmin, vmax, cmap, tline=False, adjust_cbar=False):
    df_to_map = df_phase_space.pivot('lambda','pi',magnitud) # lambda rows, pi columns
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
    #xgrid, ygrid = np.mgrid[0.05:0.5:10j, 0.05:0.95:19j]
    xgrid, ygrid = np.mgrid[min(pi):max(pi):complex(0,len(pi)), min(lamb):max(lamb):complex(0,len(lamb))]
    tck = interpolate.bisplrep(xgrid, ygrid, z)
    #xnew, ynew = np.mgrid[0.05:0.5:46j, 0.05:0.95:91j]
    xnew, ynew = np.mgrid[min(pi):max(pi):complex(0,(max(pi)-min(pi))*100+1), min(lamb):max(lamb):complex(0,(max(lamb)-min(lamb))*100+1)]
    #pi_new = [round(x[0],2) for x in xnew]
    #lamb_new = [round(y,2) for y in ynew[0]]
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
    ax.set_xlabel(r"$\pi_{1,2}$")
    ax.set_ylabel(r"$\lambda$")
    # read and plot the theoretical line:
    if(tline):
        df_Tline = get_Tline(magnitud,df_to_map)
        if not(df_Tline.empty):
            index_from = list(df_Tline['pi']).index(xnew[0][0])
            ax.plot(list(df_Tline['pi'])[index_from:], list(df_Tline['lambda'])[index_from:])
        if(adjust_cbar):
            plt.savefig(f'q1_{q1}_q2_{q2}_{magnitud}_hmap_spline_wTline_adjust_cbar.png', bbox_inches='tight', pad_inches=0.01)
        else:
            plt.savefig(f'q1_{q1}_q2_{q2}_{magnitud}_hmap_spline_wTline.png', bbox_inches='tight', pad_inches=0.01)
    else:
        if(adjust_cbar):
            plt.savefig(f'q1_{q1}_q2_{q2}_{magnitud}_hmap_spline_adjust_cbar.png', bbox_inches='tight', pad_inches=0.01)
        else:
            plt.savefig(f'q1_{q1}_q2_{q2}_{magnitud}_hmap_spline.png', bbox_inches='tight', pad_inches=0.01)
