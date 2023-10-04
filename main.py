"""Minecraft server in python 3.11
Sources for dev : 
- https://minecraft.fandom.com/wiki/Classic_server_protocol
- https://minecraft.fandom.com/wiki/Protocol_version?so=search"""

#IMPORTS - LIBRAIRIES
import socket as skt
import tkinter as tk
from tkinter.simpledialog import *
import time as tm

#IMPORTS - LOCAL
...

#GLOBAL DATAS - VARIABLES
connected_players = 0
blacklist = []
whitelist = []
whitelist_on = False

#GLOBAL DATAS - CONSTANTS
SERVER_VERSION = "Alpha-dev"    #Version of the server. For debug
CLIENT_VERSION = "1.16.5"       #Which version the client must have to connect
PROTOCOL_VERSION = 754          #Protocol version beetween server and client. See https://minecraft.fandom.com/wiki/Protocol_version?so=search for details.
PORT = 25565                    #Normal MC port
IP = skt.gethostname()
MAX_PLAYER = 5

#FUNCTIONS
...

#CLASSES
class MCServer(object):
    """Minecraft server class"""
    def __init__(self):
        """Init the server"""
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)  #socket creation
        self.socket.bind((IP, PORT))            #bind the socket

        self.misc_skt = skt.socket(skt.AF_INET, skt.SOCK_STREAM)  #socket creation
        self.misc_skt.connect("https://minecraft.net/heartbeat.jsp")

    def start(self):
        """Start the server"""
        self.socket.listen(MAX_PLAYER + 1)  #+1 is for the "connexion queue"


class World(object):
    """World class"""
    ...


#MAIN
if __name__ == "__main__":
    ...