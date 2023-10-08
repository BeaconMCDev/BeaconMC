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
state = "OFF"

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
        global state
        """Start the server"""
        log("Starting Minecraft server...", 0)
        state = "ON"
        log(f"Server version: {SERVER_VERSION}", 3)
        log(f"MC version: {CLIENT_VERSION}", 3)
        log(f"Protocol version: {PROTOCOL_VERSION}", 3)
        self.heartbeat()
        self.socket.listen(MAX_PLAYERS + 1) #+1 is for the temp connexions
        self.load_worlds()
        self.act = thread.Thread(target=self.add_client_thread)
        self.act.start()
        self.main()

    def load_worlds(self):
        """Load all of the server's world"""
        ...

    def main(self):
        """Main"""
        global state
        try:
            while state == "ON":
                tm.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
            exit(0)

    def stop(self, critical=False, reason=""):
        """stop the server"""
        if critical:
            log("Critical server stop trigered !", 100)
        log("Stopping the server...", 0)
        global state
        state = "OFF"
        if critical:
            for i in self.list_clients:
                i.disconnect(reason=tr.key("disconnect.server_crashed"))
        else:
            for i in self.list_clients:
                i.disconnect(reason=tr.key("disconnect.server_closed"))
        self.socket.close()
        ...
        if not(critical):
            exit(0)
        else:
            log("Server closed : Critical error.", 100)
            self.crash(reason)

    def crash(self, reason):
        """Generate a crash report
        Arg:
        - reason: str --> The crash message"""
        c = 0
        while os.path.exists("crash_reports/crash{0}".format(c)):
            c += 1
        with open("crash_reports/crash{0}".format(c), "w") as crashfile:
            crashfile.write("""Minecraft server in python 3.11\n________________________________________________________________________________________________________________\nA critical error advent, that force the server to stop. This crash report contain informations about the crash.\n________________________________________________________________________________________________________________\n{0}""".format(reason))



    def add_client_thread(self):
        """Thread for add clients."""
        global state
        while state == "ON":
            try:
                client_connection, client_info = self.socket.accept()
            except OSError:
                tm.sleep(0.1)
                continue
            cl = Client(client_connection, client_info, self)
            self.list_clients.append(cl)
            thr = thread.Thread(target=cl.worker)
            thr.start()
            tm.sleep(0.1)
        
    def heartbeat(self):
        """# DEPRECATED - DO NOT USE
        Heartbeat to mojangs servers. See https://minecraft.fandom.com/wiki/Classic_server_protocol#Heartbeats for details"""
        #raise DeprecationWarning("We actually have an issue for this method. It does not work.")
        request = f"POST /heartbeat.jsp?port={PORT}&max={MAX_PLAYERS}&name={MOTD}&public={public}&version={PROTOCOL_VERSION}&salt={SALT}&users={connected_players}\r\n"
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
        
    def setblock(self, base_request:bytes):
        """Analyse the setblock request and modify a block"""
        id = base_request[0]
        x = base_request[1:2]
        y = base_request[3:4]
        z = base_request[5:6]
        mode = base_request[7]
        block = base_request[8]
        #check the request
        if id != "\0x05":
            log("A non-setblock request was sent to the bad method. Something went wrong. Please leave an issue on GitHub or on Discord !", 100)
            self.stop(critical=True, reason="A non-setblock request was sent to the bad method. Something went wrong. Please leave an issue on GitHub or on Discord !")
            raise RequestAnalyseException("Exception on analysing a request : bad method used (setblock andnot unknow).")
        #TODO: Modify the block in the world
        ...
        #TODO: send to every clients the modification
        ...


class Client(object):
    def __init__(self, connexion, info, server):
        log("New client", 3)
        self.connexion = connexion
        self.info = info
        self.server = server
        self.is_op = False

    def worker(self):
        """Per client thread"""
        while True:
            self.request = self.connexion.recv(4096).decode()
            log(self.request)
            if self.request[0] == "\0x00":
                self.joining()
            elif self.request[0] == "\0x05":
                self.server.setblock(self.request)

    def joining(self):
        """When the request is a joining request"""
        self.p_version = self.request[1]
        self.username = self.request[1:64]
        self.key = self.request[65:129]
        log(f"Joining request from  {self.username} !", 0)
        if self.server.ispremium(self.username, self.key):
            log(f"{self.username} is premium.", 0)
            if connected_players < MAX_PLAYERS:
                if self.p_version == PROTOCOL_VERSION:
                    log(f"Connexion accepted for {self.username}")
                    #co ok !
                    ...
                else:
                    log(f"Failed to connect {self.username} : bad protocol version.", 0)
                    self.disconnect(tr.key("disconnect.bad_protocol"))
            else:
                log(f"Failed to connect {self.username} : server full.", 1)
                self.disconnect(tr.key("disconnect.server_full"))
        else:
            log(f"User {self.username} is not premium ! Access couldn't be gived.", 1)
            self.disconnect(tr.key("disconnect.not_premium"))

    def disconnect(self, reason=""):
        """Disconnect the player
        !!! not disconnectED !!!"""
        if reason == "":
            reason = tr.key("disconnect.default")
        self.connexion.send(f"\0x0e{bytes(reason)}".encode())
        self.server.list_client.remove(self)

    def do_spawn(self):
        """Make THIS CLIENT spawn"""
        ...
        #self.connexion.send()

    def identification(self):
        """Send id packet to the client"""
        opdico = {True:bytes("\0x64"), False: bytes("\0x00")}
        self.connexion.send(f"\0x00{bytes(PROTOCOL_VERSION)}{bytes('Python Server 1.16.5')}{bytes(MOTD)}{opdico[self.is_op]}".encode())

    def ping(self):
        """Ping sent to clients periodically."""
        self.connexion.send("\0x01".encode())

    def send_msg_to_chat(self, msg:str):
        """Post a message in the player's chat.
        Argument:
        - msg:str --> the message to post on the chat"""
        self.connexion.send(f"\0x0d\0x00{bytes(msg)}".encode())


class World(object):
    """World class"""
    ...


class Translation(object):
    def __init__(self, lang):
        self.lang = lang

    
    def en(self, key):
        """English translation"""
        dico = {"disconnect.default": "Disconnected", 
                "disconnect.server_full": "Server full.",
                "disconnect.not_premium": "Auth failed : user not premium.", 
                "disconnect.bad_protocol": "Please to connect with an other version : protocol not compatible.", 
                "disconnect.server_closed": "Server closed.", 
                "disconnect.server_crashed": "Server crashed indeed of a critical error."}
        return dico[key]
    
    def key(self, key):
        """Auto translate with key"""
        if self.lang == "en":
            return self.en(key)
        else:
            log("Lang not found !", 100)
            exit(-1)

#Exception class
class RequestAnalyseException(Exception):
    """Exception when analysing a request"""
    pass


#PRE MAIN INSTRUCTIONS
be_ready_to_log()


#MAIN
if __name__ == "__main__":
    tr = Translation("en")
    srv = MCServer()
    srv.start()
