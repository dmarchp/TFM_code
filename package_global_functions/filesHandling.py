import socket
import os
from subprocess import call

def getPCname():
    hostName = socket.gethostname()
    return hostName
    
def getExternalSSDpath():
    hostName = getPCname()
    if hostName == 'bestia' or hostName == 'david-X550LD':
        extSSDpath = '/media/david/KINGSTON'
    elif hostName == 'depaula.upc.es':
        extSSDpath = '/Volumes/KINGSTON'
    else:
        print("Unrecognized PC!")
        extSSDpath = ''
    return extSSDpath
    
def getProjectFoldername():
    return '/TFM_code'


def change_sim_input(froute, fin_file, pis=False, qs=False, lamb=None, max_time=False, N_sites=False, N_bots=False,
                     bots_per_site=False, ic=False, arena_r=False, interac_r = False, exclusion_r = None, push=False,
                     nw_model=False, nw_param=False):
    PCname = getPCname()
    if PCname == 'depaula.upc.es':
        sed_start = "sed -i'' -e "
    else:
        sed_start = 'sed -i '
    if pis:
        pis_str = ' '.join(str(pi) for pi in pis)
        sed_command = sed_start + f"'s/^pi(:) = .*/pi(:) = {pis_str}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if qs:
        qs_str = ' '.join(str(q) for q in qs)
        sed_command = sed_start + f"'s/^q(:) = .*/q(:) = {qs_str}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if lamb or lamb == 0.0:
        sed_command = sed_start + f"'s/^lambda = .*/lambda = {lamb}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if max_time:
        sed_command = sed_start + f"'s/^max_time = .*/max_time = {max_time}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if N_sites:
        sed_command = sed_start + f"'s/^N_sites = .*/N_sites = {N_sites}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if N_bots:
        sed_command = sed_start + f"'s/^N_bots = .*/N_bots = {N_bots}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if bots_per_site:
        bps_str = ' '.join(str(bps) for bps in bots_per_site)
        sed_command = sed_start + f"'s/^bots_per_site = .*/bots_per_site = {bps_str}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if ic:
        ic_call = f"sed -i'' -e '34s/.*/random_bots_per_site = \"{ic}\"/' "+froute+fin_file
        call(ic_call, shell=True)
    # Quenched simulation parametrs only #
    if arena_r:
        sed_command = sed_start + f"'s/arena_r.*/arena_r = {arena_r}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if interac_r:
        sed_command = sed_start + f"'s/interac_r.*/interac_r = {interac_r}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if exclusion_r or exclusion_r == 0.0:
        sed_command = sed_start + f"'s/exclusion_r.*/exclusion_r = {exclusion_r}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if push:
        sed_command = sed_start + f"'s/push.*/push = {push}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    # Network simulation parameters only #
    if nw_model:
        sed_command = sed_start + f"'s/nw_model.*/nw_model = \"{nw_model}\"/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if nw_param:
        sed_command = sed_start + f"'s/nw_param.*/nw_param = {nw_param}/' "
        call(f'{sed_command}'+froute+fin_file, shell=True)
    if os.path.exists(froute+fin_file+'-e'):
        call(f'rm {froute+fin_file}-e', shell=True)


# bots per site simulation input (not exactly files handling but ok...)
def prepare_ic(N, Nsites, ic):
    bots_per_site = [0]*(Nsites+1)
    if ic == 'N':
        bots_per_site[0] = N
    elif ic == 'E':
        bots_per_site[1:] = [int(N/Nsites)]*Nsites
        remaining = N%Nsites
        bots_per_site[1:1+remaining] = [b+1 for b in bots_per_site[1:1+remaining]]
    elif ic == 'E0':
        bots_per_site = [int(N/(Nsites+1))]*(Nsites+1)
        remaining = N%(Nsites+1)
        bots_per_site[0:0+remaining] = [b+1 for b in bots_per_site[0:0+remaining]]
    elif ic[0] == 'p': # inputs such as p50-25-25
        icClean = ic[1:]
        props = [int(p) for p in icClean.split('-')]
        sumProps = sum(props)
        if sumProps != 100:
            print('Problem setting the initial condition!!')
            return
        bots_per_site = [int(p*N/100) for p in props]
        remaining = (N-sum(bots_per_site))%(Nsites+1)
        bots_per_site[0:0+remaining] = [b+1 for b in bots_per_site[0:0+remaining]]
        # comprova que no la liis!!
        if sum(bots_per_site) != N:
            print('Bad generation of bots per site!!!!!')
    return bots_per_site

    

