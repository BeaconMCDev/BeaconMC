"""Minecraft server in python 3.11
Sources for dev : 
- https://minecraft.fandom.com/wiki/Classic_server_protocol
- https://minecraft.fandom.com/wiki/Protocol_version?so=search"""

#IMPORTS - LIBRAIRIES
import socket as skt
import tkinter as tk
from tkinter.simpledialog import *
import time as tm
import random as rdm

#IMPORTS - LOCAL
...

#GLOBAL DATAS - VARIABLES
connected_players = 0
blacklist = []
whitelist = []
public = True
users = []

#GLOBAL DATAS - CONSTANTS
SERVER_VERSION = "Alpha-dev"    #Version of the server. For debug
CLIENT_VERSION = "1.16.5"       #Which version the client must have to connect
PROTOCOL_VERSION = 754          #Protocol version beetween server and client. See https://minecraft.fandom.com/wiki/Protocol_version?so=search for details.
PORT = 25565                    #Normal MC port
IP = skt.gethostname()
MAX_PLAYERS = 5
SALT = "wo6kVAHjxoJcInKx"
MOTD = "My%20Server"

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
        self.misc_skt.connect(("minecraft.net", 80))


    def start(self):
        """Start the server"""
        url = "/heartbeat.jsp"

        query_parameters = f"port={PORT}&max={MAX_PLAYERS}&name={MOTD}&public={public}&version={PROTOCOL_VERSION}&salt={SALT}&users={connected_players}"
        request = f"GET {url}?{query_parameters} HTTP/1.0\r\nHost: https://minecraft.net\r\n\r\n"
        self.misc_skt.sendall(request.encode())
        print(self.misc_skt.recv(4096))
        self.socket.listen(MAX_PLAYERS + 1)  #+1 is for the "connexion queue"



class World(object):
    """World class"""
    ...


#MAIN
if __name__ == "__main__":
    srv = MCServer()
    srv.start()