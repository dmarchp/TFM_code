import socket
import os

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
