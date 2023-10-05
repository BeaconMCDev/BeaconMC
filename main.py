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
import sys
import os

#IMPORTS - LOCAL
...

#GLOBAL DATAS - VARIABLES
connected_players = 0
blacklist = []
whitelist = []
public = True
users = []
logfile = ""

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
def log(msg:str, type:int=-1):
    """Types:
    - 0: info
    - 1: warning
    - 2: error
    - 3: debug
    - other: unknow"""
    if type == 0:
        t = "INFO"
    elif type == 1:
        t = "WARN"
    elif type == 2:
        t = "ERROR"
    elif type == 3:
        t = "DEBUG"
    else:
        t = "UNKNOW"
    time = gettime()
    text = f"[{time}] [Server/{t}]: {msg}"
    print(text)
    with open(logfile, "+a") as file:
        file.write(text + "\n")

def gettime():
    return tm.asctime(tm.localtime(tm.time())).split(" ")[-2]

def be_ready_to_log():
    global logfile
    nb = 1
    while os.path.exists(f"logs/log{nb}.log"):
        nb += 1
    logfile = f"logs/log{nb}.log"
    
    

#CLASSES
class MCServer(object):
    """Minecraft server class"""
    def __init__(self):
        """Init the server"""
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)  #socket creation
        self.socket.bind((IP, PORT))            #bind the socket

    def start(self):
        """Start the server"""
        log("Starting Minecraft server...", 0)
        log(f"Server version: {SERVER_VERSION}", 3)
        log(f"MC version: {CLIENT_VERSION}", 3)
        log(f"Protocol version: {PROTOCOL_VERSION}", 3)
        log("Starting hearbeat...", 0)

        url = "/heartbeat.jsp"
        query_parameters = f"port={PORT}&max={MAX_PLAYERS}&name={MOTD}&public={public}&version={PROTOCOL_VERSION}&salt={SALT}&users={connected_players}"
        request = f"GET {url}?{query_parameters} HTTP/1.0\r\nHost: https://minecraft.net\r\n\r\n"
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(("minecraft.net", 80))
            s.sendall(request.encode())
            resp = s.recv(4096)
            if resp != IP:
                log("An issue advent during the heartbeat Mojang server side. See the following response for details : ", 2)
                log(resp)
        self.socket.listen(MAX_PLAYERS + 1)  #+1 is for the "connexion queue"



class World(object):
    """World class"""
    ...


#PRE MAIN INSTRUCTIONS
be_ready_to_log()


#MAIN
if __name__ == "__main__":
    srv = MCServer()
    srv.start()