import numpy as np

# Find the stationary time of the time evolution from solving an ODE;
def evoTimeDeriv_solve_ivp(sol, getFullEvo=False, getStatTime=True, thresh=1e-4, discard_initial=0.0):
    '''
    recieves the full output sol from solve_ivp (i.e sol.t, sol.y[...] ...)
    '''
    evo_derivs = []
    for j in range(len(sol.y)):
        if getFullEvo:
            dfj = []
        if getStatTime:
            statTimej = []
        for i in range(len(sol.t)):
            if i == 0: # forward derivative at timestep 0
                deriv = (sol.y[j][1]-sol.y[j][0])/(sol.t[1]-sol.t[0])
            elif i == len(sol.t)-1: # backwards derivative at the last timestep
                deriv = (sol.y[j][-1]-sol.y[j][-2])/(sol.t[-1]-sol.t[-2])
            else: # central derivative at the last point
                deriv = (sol.y[j][i+1]-sol.y[j][i-1])/(sol.t[i+1]-sol.t[i-1])
            if getFullEvo:
                dfj.append(deriv)
            if getStatTime:
                if abs(deriv) <= thresh and sol.t[i] >= discard_initial:
                    statTimej.append(sol.t[i])
                    break
        if getFullEvo:
            evo_derivs.append(dfj)
    if getFullEvo:
        return evo_derivs
    if getStatTime:
        return max(statTimej)
    
def evoTimeDeriv_general(tarray, yarray, getFullEvo=False, getStatTime=True, thresh=1e-4):
    # central derivative for all timesteps inbetween first to last:
    evoDeriv = (yarray[2:] - yarray[:-2])/(tarray[2:] - tarray[:-2])
    # forward derivative for the first timestep:
    evoDeriv = np.insert(evoDeriv, 0, (yarray[1]-yarray[0])/(tarray[1]-tarray[0]))
    # backward derivative for the last timestep:
    evoDeriv = np.insert(evoDeriv, -1, (yarray[-1]-yarray[-2])/(tarray[-1]-tarray[-2]))
    statTime = tarray[abs(evoDeriv) <= thresh][0]
    if getFullEvo and getStatTime:
        return statTime, evoDeriv
    elif not getFullEvo and getStatTime:
        return statTime
    

# buscar la funcion que feia servir per les evolucions estocastiques i generalitzar-la per tot
# o bé no imposar un threshold com a parametre a l'anterior funció, si no veure com de petita arriba
# a ser la derivada al plateau final i fer servir aquell valor com a referència




# Find the stationary time of the time evolution from a stochatic simulation;