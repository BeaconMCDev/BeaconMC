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
import os
import threading as thread
import hashlib #for md5 auth system

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
SALT_CHAR = "a-z-e-r-t-y-u-i-o-p-q-s-d-f-g-h-j-k-l-m-w-x-c-v-b-n-A-Z-E-R-T-Y-U-I-O-P-Q-S-D-F-G-H-J-K-L-M-W-X-C-V-B-N-0-1-2-3-4-5-6-7-8-9".split("-")
SALT = ''.join(rdm.choice(SALT_CHAR) for i in range(15))
MOTD = "My%20Server"
DEBUG = True                    #debug mode enabled

#FUNCTIONS
def log(msg:str, type:int=-1):
    """Types:
    - 0: info
    - 1: warning
    - 2: error
    - 3: debug
    - 100: critical
    - other: unknow"""
    if type == 0:
        t = "INFO"
    elif type == 1:
        t = "WARN"
    elif type == 2:
        t = "ERROR"
    elif type == 3:
        t = "DEBUG"
        if not(DEBUG):
            return
    elif type == 100:
        t = "CRITICAL"
    else:
        t = "UNKNOW"
    time = gettime()
    text = f"[{time}] [Server/{t}]: {msg}"
    print(text)
    with open(logfile, "+a") as file:
        file.write(text + "\n")

    return

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
        self.list_info = []
        self.list_clients = []

    def start(self):
        """Start the server"""
        log("Starting Minecraft server...", 0)
        log(f"Server version: {SERVER_VERSION}", 3)
        log(f"MC version: {CLIENT_VERSION}", 3)
        log(f"Protocol version: {PROTOCOL_VERSION}", 3)
        log("Starting hearbeat...", 3)
        self.heartbeat()
        self.socket.listen(MAX_PLAYERS + 1) #+1 is for the temp connexions
        self.main()

    def main(self):
        """Main loop for the server."""
        while True:
            client_connection, client_info = self.socket.accept()
            cl = Client(client_connection, client_info, self)
            thr = thread.Thread(target=cl.worker)
            thr.start()
            tm.sleep(0.1)
        
    def heartbeat(self):
        """Heartbeat to mojangs servers. See https://minecraft.fandom.com/wiki/Classic_server_protocol#Heartbeats for details"""

        request = f"GET /heartbeat.jsp?port={PORT}&max={MAX_PLAYERS}&name={MOTD}&public={public}&version={PROTOCOL_VERSION}&salt={SALT}&users={connected_players}\r\n"
        with skt.socket(skt.AF_INET, skt.SOCK_STREAM) as s:
            s.connect(("minecraft.net", 80))
            s.sendall(request.encode())
            resp = s.recv(4096)
            if resp != IP:
                log("An issue advent during the heartbeat Mojang server side. See the following response for details : ", 100)
                log(resp)
                exit(-1)
        log(resp)
        log("Done !", type=3)

    def is_premium(self, username:str, key:str):
        """Check if the user is a premium user.
        See https://minecraft.fandom.com/wiki/Classic_server_protocol#User_Authentication"""
        if key == hashlib.md5(SALT + username):
            #premium user
            return True
        else:
            #cracked use
            return False

class Client(object):
    def __init__(self, connexion, info, server):
        self.connexion = connexion
        self.info = info
        self.server = server

    def worker(self):
        """Per client thread"""
        while True:
            self.request = self.connexion.recv(4096).decode()
            if self.request[0] == "\x00":
                self.joining()

    def joining(self):
        """When the request is a joining request"""
        self.p_version = self.request[1]
        self.username = self.request[2]
        self.key = self.request[3]
        if self.server.ispremium(self.username, self.key):
            #User premium
            if connected_players < MAX_PLAYERS:
                if self.p_version == PROTOCOL_VERSION:
                    #co ok !
                    ...
                else:
                    self.disconnect(tr.key("disconnect.bad_protocol"))
            else:
                self.disconnect(tr.key("disconnect.server_full"))
        else:
            self.disconnect(tr.key("disconnect.not_premium"))

    def disconnect(self, reason=""):
        """Disconnect the player
        !!! not disconnectED !!!"""
        if reason == "":
            reason = tr.key("disconnect.default")
        self.connexion.send(f"\x0e{bytes(reason)}".encode())

    def do_spawn(self):
        """Make THIS CLIENT spawn"""
        ...
        #self.connexion.send()



class World(object):
    """World class"""
    ...


class Translation(object):
    def __init__(self, lang):
        self.lang = lang

    
    def en(self, key):
        dico = {"disconnect.default": "Disconnected", 
                "disconnect.server_full": "Server full.",
                "disconnect.not_premium": "Auth failed : user not premium.", 
                "disconnect.bad_protocol": "Please to connect with an other version : protocol not compatible."}
        return dico[key]
    
    def key(self, key):
        if self.lang == "en":
            return self.en(key)
        else:
            log("Lang not found !", 100)
            exit(-1)


#PRE MAIN INSTRUCTIONS
be_ready_to_log()


#MAIN
if __name__ == "__main__":
    tr = Translation("en")
    srv = MCServer()
    srv.start()
