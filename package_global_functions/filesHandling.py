import socket
import os

def getPCname():
    hostName = socket.gethostname()
    return hostName
    
def getExternalSSDpath():
    hostName = getPCname()
    if hostName == 'bestia':
        extSSDpath = '/media/david/KINGSTON'
    elif hostName == 'davidASUS': # CANVIAR PEL NOM CORRECTE
        extSSDpath = '/media/aaa/KINGSTON'
    return extSSDpath
