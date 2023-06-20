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


def change_sim_input(froute, fin_file, pis=False, qs=False, lamb=False, max_time=False, N_sites=False, N_bots=False,
                     bots_per_site=False, ic=False):
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
    if lamb:
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
    

