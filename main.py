"""Minecraft server in python 3.11
Source for dev : 
- https://wiki.vg"""

print("_________________________________________________________\nStarting BeaconMC 1.19.4\n_________________________________________________________")

print("Importing librairies...")
#IMPORTS - LIBRAIRIES
import socket as skt
import time as tm
import random as rdm
import plugins.modulable_pluginsystem as mplsys
from typing import Literal
import threading as thread
import os
import hashlib #for md5 auth system
import platform
import pluginapi
import json
import struct
import uuid
try:
    import nbtlib
except ModuleNotFoundError:
    print("Installing missing library...")
    os.system("pip install nbtlib")
    import nbtlib
    print("Done")

dt_starting_to_start = tm.time()
lthr = []

#BASE ERROR
class OSNotCompatibleError(OSError):
    pass

#CONFIG READING
print("Reading the config file...")
with open("config.txt", "r") as config:
    dt = None
    while dt != "":
        dt = config.readline()
        if dt == "":
            break
        dt = dt.split("=")
        if dt[1][-1] == "\n":
            arg = dt[1][:-1]
        else:
            arg = dt[1]
        if dt[0] == "whitelist":
            dico = {"true": True, "false": False}
            public = dico[arg]
            print(f"Whitelist: {arg}")
        elif dt[0] == "max_players":
            MAX_PLAYERS = int(arg)
            print(f"Max players: {arg}")
        elif dt[0] == "motd":
            MOTD = arg
            print(f"MOTD: {arg}")
        elif dt[0] == "debug_mode":
            dico = {"true": True, "false": False}
            DEBUG = dico[arg]
            print(f"Debug mode: {arg}")
        elif dt[0] == "lang":
            lang = arg
            print(f"Lang: {arg}")
        elif dt[0] == "online_mode":
            dico = {"true": True, "false": False}
            ONLINE_MODE = dico[arg]
        else:
            continue

print("Done.")
print("Setting up the server...")
print("Checking OS compatibility...")
COMPATIBLE_OS = ["Windows", "Linux"]
OS = platform.system()
if OS in COMPATIBLE_OS:
    if OS == "Linux":
        SEP = '/'
    elif OS == "Windows":
        SEP = "\\"
else:
    raise OSNotCompatibleError(f"OS {OS} is not compatible ! Please use Linux or Windows !")
print(f"OS {OS} is compatible !")

#GLOBAL DATAS - VARIABLES
connected_players = 0
blacklist = []
whitelist = []
#public = True
users = []
logfile = ""
state = "OFF"

#GLOBAL DATAS - CONSTANTS
#################################
###          READ THIS       ####
### don't touch this section ####
#################################

SERVER_VERSION = "Alpha-dev"    #Version of the server. For debug
CLIENT_VERSION = "1.19.4"       #Which version the client must have to connect
PROTOCOL_VERSION = 762          #Protocol version beetween server and client. See https://minecraft.fandom.com/wiki/Protocol_version?so=search for details.
PORT = 25565                    #Normal MC port
IP = "0.0.0.0"
#MAX_PLAYERS = 5
SALT_CHAR = "a-z-e-r-t-y-u-i-o-p-q-s-d-f-g-h-j-k-l-m-w-x-c-v-b-n-A-Z-E-R-T-Y-U-I-O-P-Q-S-D-F-G-H-J-K-L-M-W-X-C-V-B-N-0-1-2-3-4-5-6-7-8-9".split("-")
SALT = ''.join(rdm.choice(SALT_CHAR) for i in range(15))
CONFIG_TO_REQUEST = {"\u00A7": "\xc2\xa7", "§": "\xc2\xa7"}
#log counts
errors = 0
warnings = 0
debug = 0
info = 0
critical = 0
unknow = 0

print("")

def log(msg:str, type:int=-1):
    """Types:
    - 0: info
    - 1: warning
    - 2: error
    - 3: debug
    - 4: chat
    - 100: critical
    - other: unknow"""
    global errors, warnings, debug, info, critical, unknow

    if type == 0:
        t = "INFO"
        info += 1
    elif type == 1:
        t = "WARN"
        warnings += 1
    elif type == 2:
        t = "ERROR"
        errors += 1
    elif type == 3:
        t = "DEBUG"
        if not(DEBUG):
            return
        else:
            debug += 1
    elif type == 4:
        t = "CHAT"
    elif type == 100:
        t = "CRITICAL"
        critical += 1
    else:
        unknow += 1
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
    print("Log system ready !")

def encode(msg:str):
    """Convert quickly a string into bytes that will be sended to the client."""
    return msg.encode()
    
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
#CLASSES
class MCServer(object):
    """Minecraft server class"""

    SERVER_VERSION = SERVER_VERSION
    CLIENT_VERSION = CLIENT_VERSION  
    PROTOCOL_VERSION = PROTOCOL_VERSION
    PORT = PORT              
    IP = IP
    ONLINE_MODE = ONLINE_MODE

    def __init__(self):
        """Init the server"""
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)  #socket creation
        self.socket.bind((IP, PORT))            #bind the socket
        self.list_info = []
        self.list_clients = []
        self.list_worlds = []
        try:
            with open("eula.txt", "r") as eula_file:
                if eula_file.read() == "eula=true":
                    pass
                else:
                    log("You need to agree the Minecraft EULA to continue.", 1)
                    log("The conditions are readable here : https://www.minecraft.net/fr-ca/eula. To accept it, go to eula.txt and write 'eula=true'.", 1)
                    log("The server will not start until the EULA is not accepted, and if this script is modified we will not support or help you.", 1)
                    self.stop(False, reason="You need to accept Minecraft eula to continue.")
                return
        except Exception as e:
            print(f"{type(e)} : {e}")
            log("The eula.txt file was not found, or the server was modified !", 1)
            log("You need to agree the Minecraft EULA to continue.", 2)
            log("The conditions are readable here : https://www.minecraft.net/fr-ca/eula. To accept it, go to eula.txt and write 'eula=true'.", 1)
            log("The server will not start until the EULA is not accepted, and if this script is modified we will not support or help you.", 1)
            self.stop(False, reason="You need to accept Minecraft eula to continue.")
            return
        

    def worlds_analyse(self):
        """Search for worlds in the worlds folder.
        Return a list str that are the world name."""
        log("Analysing worlds...", 3)
        items_list = os.listdir(f"{os.getcwd()}{SEP}worlds")
        lst_world = []
        for item in items_list:
            try:
                name, extention = item.split(".")
            except ValueError:
                continue
            if extention == ".mcworld":
                lst_world.append(name)
        log(f"{len(lst_world)} worlds found !", 3)
        return lst_world
    
    def log(self, msg:str, type:int=-1):
        """An alternative of main.log(). Don't delete, used by plugins."""
        log(msg, type)

    def start(self):
        global state
        """Start the server"""
        log("Starting Minecraft server...", 0)
        state = "ON"
        log(f"Server version: {SERVER_VERSION}", 3)
        log(f"MC version: {CLIENT_VERSION}", 3)
        log(f"Protocol version: {PROTOCOL_VERSION}", 3)
        #self.heartbeat()

        self.load_plugins()

        self.socket.listen(MAX_PLAYERS + 1) #+1 is for the temp connexions
        self.load_worlds()
        self.act = thread.Thread(target=self.add_client_thread)
        self.act.start()
        lthr.append(self.act)
        self.main()

    def load_plugins(self):
        """Load the plugins"""
        self.PLUGIN_ALLOWED = mplsys.ENABLE_PLUGINS
        self.PLUGIN_LIST = mplsys.PLUGIN_LIST

        for pl in self.PLUGIN_LIST:
            pl.set_server(self)
            if pl._on_load():
                pl.on_load()
            

    def load_worlds(self):
        """Load all of the server's worlds"""
        log("Loading worlds...", 0)
        pre_list_worlds = self.worlds_analyse()
        for world in pre_list_worlds:
            w_class = World(world)
            w_class.load()
            self.list_worlds.append(w_class)
        log(f"DONE ! Server successfully started on {round(tm.time() - dt_starting_to_start, 2)} seconds.", 0)

    def main(self):
        """Main"""
        global state
        try:
            while state == "ON":
                tm.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
            exit(0)

    def stop(self, critical_stop=False, reason="Server closed"):
        """stop the server"""
        if critical_stop:
            log("Critical server stop trigered !", 100)
        log("Stopping the server...", 0)
        global state
        state = "OFF"
        global lthr
        log("Disconnecting all the clients...", 0)
        if critical_stop:
            for i in self.list_clients:
                i: Client
                i.disconnect(reason=tr.key("disconnect.server_crashed"))
        else:
            for i in self.list_clients:
                i.disconnect(reason=tr.key("disconnect.server_closed"))
        log("Closing socket...", 0)
        self.socket.close()
        log("Stopping all tasks...", 0)
        for t in lthr:
            t: thread.Thread
            t.join()
        
        ...
        
        if not(critical_stop):
            log(f"Server closed with {critical} criticals, {errors} errors, {warnings} warnings, {info} infos and {unknow} unknown logs : {reason}", 0)
            exit()
        else:
            log(f"Server closed with {critical} criticals, {errors} errors, {warnings} warnings, {info} infos and {unknow} unknown logs : {reason}", 100)
            self.crash(reason)
            exit(-1)


    def crash(self, reason):
        """Generate a crash report
        Arg:
        - reason: str --> The crash message"""
        c = 0
        while os.path.exists("crash_reports/crash{0}".format(c)):
            c += 1
        with open("crash_reports/crash{0}".format(c), "w") as crashfile:
            crashfile.write(f""" BeaconMC {SERVER_VERSION}\n\nFor Minecraft {CLIENT_VERSION}\n________________________________________________________________________________________________________________\nA critical error advent, that force the server to stop. This crash report contain informations about the crash.\n________________________________________________________________________________________________________________\nThe server crashed because of the following cause : {reason}\nDebug mode : {DEBUG}""")


    def add_client_thread(self):
        """Thread for add clients."""
        global state
        self.client_id_count = 0
        while state == "ON":
            try:
                client_connection, client_info = self.socket.accept()
            except OSError:
                tm.sleep(0.1)
                continue
            cl = Client(client_connection, client_info, self)
            self.list_clients.append(cl)
            thr = thread.Thread(target=cl.client_thread, args=[self.client_id_count])
            thr.start()
            lthr.append(thr)
            self.client_id_count += 1
            tm.sleep(0.1)

    def is_premium(self, username:str):
        """Check if the user is a premium user. Return a boolean"""
        import libs.mojangapi as mojangapi

        accchecker = mojangapi.Accounts()
        return accchecker.check(self.username)

        
    def setblock(self, base_request:bytes):
        """Analyse the setblock request and modify a block"""
        id = base_request[0]
        x = base_request[1:2]
        y = base_request[3:4]
        z = base_request[5:6]
        mode = base_request[7]
        block = base_request[8]
        #check the request
        if id != "\x05":
            log("A non-setblock request was sent to the bad method. Something went wrong. Please leave an issue on GitHub or on Discord !", 100)
            self.stop(critical=True, reason="A non-setblock request was sent to the bad method. Something went wrong. Please leave an issue on GitHub or on Discord !")
            raise RequestAnalyseException("Exception on analysing a request : bad method used (setblock andnot unknow).")
        #TODO: Modify the block in the world
        ...
        #TODO: send to every clients the modification
        ...

    def post_to_chat(self, message:str, author:str=""):
        """Post a message in all player's chat
        Args:
        - message: str --> the message to send
        - author: str --> the author of the message: by default ""."""
        if author == "":
            msg = message
        else:
            msg = f"{author}: {message}"
        for p in self.list_clients:
            p.send_msg_to_chat(msg)
        log(msg, 4)

    def mp(self, message:str, addressee:str, author:str):
        """Send a mp to 1 player
        Args:
        - message:str --> the message to send in mp
        - addressee:str --> player that will receive msg
        - author:str --> the author of the msg: by default ""."""

        pl = self.find_player_by_username(addressee)
        msg = f"{author} --> you: {message}"
        pl.send_msg_to_chat(msg)
        log(f"{author} --> {pl}: {message}", 4)
        for pl in self.PLUGIN_LIST:
            pl.on_mp(message=message, source=author, addressee=addressee)

    def find_player_by_username(self, username:str):
        """Find the player socket with the username.
        Arg:
        - username:str --> the username of the player.
        - Returns player socket
        - return None if no player found
        - Raise error if more than 1 player is found"""
        lst = []
        for p in self.list_clients:
            if p.username == username:
                lst.append(p)
        if len(lst) == 0:
            return None
        elif len(lst) == 1:
            return lst[0]
        else:
            raise TwoPlayerWithSameUsernameException(f"2 players with the same username {username} were found.")
        

class PacketException(Exception):
    pass

class Packet(object):
    # DANGER | DO NOT TOUCH
    SEGMENT_BITS = 0x7F
    CONTINUE_BIT = 0x80

    def __init__(self, socket: skt.socket, direction: Literal["-OUTGOING", "-INCOMING"], typep: hex=None, packet:bytes=None, args:tuple = None):
        self.type = typep
        self.socket = socket
        self.direction = direction
        self.packet = packet
        self.args = args

        #if packet == None or b"" and typep == None:
        #    raise PacketException(f"No information provided in the Packet instance {self}")
        if direction == "-INCOMING":
            self.incoming_packet()
        elif direction == "-OUTGOING":
            self.outgoing_packet()

    def incoming_packet(self):
        if self.type == None and not(self.packet == b""):
            self.unpack()

    def unpack(self):
        lenth = self.packet[0]
        id = self.packet[1]
        other = self.packet[2:]
        self.type = id
        self.args = other
        return lenth

    def outgoing_packet(self):
        ...

    def pack_varint(self, d:int):
        o = b""
        #if d >= 255:
        #    o = d.to_bytes(2, byteorder="little")
        #else:
        #test
        if True:
            while True:
                b = d & 0x7F
                d >>= 7
                o += struct.pack("B", b | (0x80 if d > 0 else 0))
                if d == 0:
                    break
        return o
    
    def pack_data(self, d):
        h = self.pack_varint(len(d))
        if type(d) == str:
            d = bytes(d, "utf-8")
        return h + d

    def send(self):
        if self.direction == "-OUTGOING":
            self.socket.send(self.__repr__())
        else:
            raise PacketException("Incoming packet tryied to be sended")

    def __repr__(self) -> bytes:
        out = self.pack_varint(self.type)   #pack the type
        for i in self.args:
            if type(i) == "<class 'int'>":
                out += self.pack_varint(len(self.pack_varint(i))) + self.pack_varint(i)
            else:
                out += self.pack_data(i)
        out = self.pack_varint(len(out)) + out
        return out
    
    def __str__(self):
        return self.__repr__().decode()

########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
class Client(object):
    def __init__(self, connexion: skt.socket, info, server:MCServer):
        log("New client", 3)
        self.connexion = connexion
        self.info = info
        self.server = server
        self.is_op = False
        self.x = None
        self.y = None
        self.z = None
        self.connected = True
        self.state = 0

    def on_heartbeat(self):
        """Id of the packet: 0x00"""
        client_protocol_version = self.request[1:]
        ...

    def on_login_start(self):
        """Starting the login in (rq C --> S)"""
        self.request
        ...

    def client_thread(self, id):
        """Per client thread"""
        self.id = id
        try:
            while self.connected and state == "ON":
                try:
                    self.request = self.connexion.recv(4096)
                except:
                    continue
                if self.request == "":
                    continue
                log(self.request, 3)

                if self.request == b"\x00":
                    pass #status ping

                self.packet = Packet(self.connexion, "-INCOMING", packet=self.request)
                
                if self.packet.type == 0:
                    if self.packet.args[-1] == 1:
                        self.SLP()
                        self.connexion.close()
                        self.connected = False
                        self.server.list_clients.remove(self)
                    else:
                        self.SLP()              
                        self.connexion.close()   # temp fix
                        self.connected = False
                        continue
                        self.joining()
                elif self.packet.type == 1:
                    self.SLP()
                    self.connexion.close()
                    self.connected = False
                elif self.packet.type == 3:
                    if self.state == 1:
                        ...
                    else:
                        log(f"BadPacket.", 1)
                else:
                        tm.sleep(1)
                        continue
                        c = -1
                        u = ""
                        while self.request[c] != "\x0f":
                            u = self.request[c] + u
                            c -= 1
                        self.username = u
                        self.joining()


                #if self.request[0] == "\x05":
                #    #setblock message
                #    self.server.setblock(self.request)
                #elif self.request[0] == "\x08":
                #    #pos message
                #    self.update_pos()
                #elif self.request[0] == "\x0d":
                #    #chat message
                #    if self.request[2] == "/":#surely not that
                #        ... #cmd
#   
                #    self.server.post_to_chat(author=self.username, message=self.request[1:])
                #elif self.request[:4] == "\x13\x00\xf2\x05\x0c":
                #    if self.request[-5:] == "\xd5\x11\x01\x01\x00":
                #        #server list request
                #        self.connexion.send(bytes('\xca\x01\x00\xc7\x01{"previewsChat":false,"description":{"text":"{0}"},"players":{"max":{1},"online":{2}},"version":{"name":"{3}","protocol":{4}}}'.format(self.treat(MOTD), MAX_PLAYERS, connected_players, CLIENT_VERSION, PROTOCOL_VERSION)))
                #    else:
                #        c = -1
                #        u = ""
                #        while self.request[c] != "\x0f":
                #            u = self.request[c] + u
                #            c -= 1
                #        self.username = u
                #        self.joining()
            self.server.list_clients.remove(self)
        except Exception as e:
            raise e
        
    def status_request(self):
        ...

    def bad_version(self):
        """Called to disconnect the connecting client that has a bad protocol version"""
        log("A client used a bad version. Disconnecting this client...", 0)
        self.connexion.send(encode(f'E\x00C{"translate":"multiplayer.disconnect.incompatible","with":["{CLIENT_VERSION}"]}'))
        self.connected = False
        self.connexion.close()
        self.server.list_client.remove(self)
        log("Client disconnected: bad Minecraft version", 0)
        del(self)

    def treat(self, msg):
        """Check and modify the message gived in argument in the goal of be readable by the client."""
        final = ""
        for char in msg:
            try:
                final += CONFIG_TO_REQUEST[char]
            except IndexError:
                final += char
        return final

    def update_pos(self):
        """update the client pos with the request"""
        ...

    def unpack_uuid(self, d:bytes):
        msb = struct.unpack('>Q', d[:8])[0]
        lsb = struct.unpack('>Q', d[8:])[0]
        return uuid.UUID(int=(msb << 64) | lsb)

    def joining(self):
        """When the request is a joining request"""
        self.username = self.packet.args[0]
        self.uuid = self.packet.args[1]
        log(f"Player {self.username} with uuid {self.uuid} is loging in !")

        if connected_players >= MAX_PLAYERS:
            r = tr.key("disconnect.server_full")
            log(f"Disconnecting {self.username}: {r}", 0)
            self.disconnect(tr.key("disconnect.server_full"))
            return
        #HOW TO GET THE PROTOCOL VERSION ?
        if not(PROTOCOL_VERSION == PROTOCOL_VERSION):
            r = tr.key("disconnect.bad_protocol")
            log(f"Disconnecting {self.username} : {r}.", 0)
            self.bad_version()
            return
        if not(self.server.is_premium(self.username)):
            r = tr.key("disconnect.not_premium")
            log(f"Disconnecting {self.username} : {r}.", 0)
            self.disconnect(tr.key("disconnect.not_premium"))
            return
        
        if ONLINE_MODE:
            
            p_response = Packet(self.connexion, direction="-OUTGOING", typep=1, args=("serverid", b"publick key", "verify token", ONLINE_MODE))
            log(p_response, 3)
            p_response.send()

        packet_r = Packet(self.connexion, "-OUTGOING", typep=2, args=(self.uuid, self.username, 0, False))
        log(packet_r, 0)
        packet_r.send()
        self.state = 1


        """
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
                    log(f"Failed to connect {self.username} : bad version.", 0)
                    #self.disconnect(tr.key("disconnect.bad_protocol"))   :-(
                    self.bad_version()
            else:
                log(f"Failed to connect {self.username} : server full.", 1)
                self.disconnect(tr.key("disconnect.server_full"))
        else:
            log(f"User {self.username} is not premium ! Access couldn't be gived.", 1)
            self.disconnect(tr.key("disconnect.not_premium"))"""

    def disconnect(self, reason=""):
        """Disconnect the player
        !!! not disconnectED !!!"""
        self.connected = False
        if reason == "":
            reason = tr.key("disconnect.default")
        self.connexion.send(f"\x0e{reason}".encode("utf-8"))
        self.connexion.close()
        self.server.list_clients.remove(self)
        del(self)

    def do_spawn(self):
        """Make THIS CLIENT spawn"""
        ...
        #self.connexion.send()

    def identification(self):
        """Send id packet to the client"""
        opdico = {True:bytes("\x64"), False: bytes("\x00")}
        self.connexion.send(f"\x00{bytes(PROTOCOL_VERSION)}{bytes('Python Server 1.19.4')}{bytes(MOTD)}{opdico[self.is_op]}".encode())

    def ping(self):
        """Ping sent to clients periodically."""
        self.connexion.send("\x01".encode())

    def int_to_hex_escape(n):
        if n < 0:
            raise ValueError("L'entier doit être positif.")

        hex_string = n.to_bytes((n.bit_length() + 7) // 8, 'big').hex()
        escaped_string = ''.join(f'\\x{hex_string[i:i+2]}' for i in range(0, len(hex_string), 2))
        return escaped_string



    def SLP(self):
        log("Received ping", 3)

        from base64 import b64encode
        try :
            with open('server-icon.png', 'rb') as image_file :
                favicon = b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            log("Server icon not found, using default", 1)
            favicon = "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"
            response = {
            "version": {"name": CLIENT_VERSION, "protocol": PROTOCOL_VERSION},
            "players": {"max": MAX_PLAYERS, "online": len(self.server.list_clients), "sample": [{"name": "FewerElk", "id": "16dcb929-b271-4db3-9cc6-059a851fcce1"}]},
            "description": {"text": MOTD},
            "favicon": "data:image/png;base64," + favicon,
            "modinfo": {"type": "FML", "modlist": []},
            "enforcesSecureChat": True,
            "previewsChat": True
        }

        response_str = json.dumps(response)

        packet_response = Packet(socket=self.connexion, direction="-OUTGOING", typep=0, args=(response_str, ))
        
        packet_response.send()

    def on_SLP(self):
        log("Event 'on server list ping' triggered !", 3)
        request = f'\xca\x01\x00\xc7\x01\u007b"previewsChat":false,"description":\u007b"text":"{MOTD}"\u007d,"players":\u007b"max":{MAX_PLAYERS},"online":{len(self.server.list_clients)}\u007d,"version":\u007b"name":"{CLIENT_VERSION}","protocol":{PROTOCOL_VERSION}\u007d\u007d'        
        request = encode(request)
        self.connexion.send(request, 1024)

            #self.connexion.send(f'0x01{"version":{"name":"1.19.4","protocol":762},"players":{"max":100,"online":5,"sample":[{"name":"thinkofdeath","id":"4566e69f-c907-48ee-8d71-d7ba5aa00d20"}]},"description":{"text":"Hello world"},"favicon":"data:image/png;base64,<data>","enforcesSecureChat":true,"previewsChat":true}')
    def send_msg_to_chat(self, msg:str):
        """Post a message in the player's chat.
        Argument:
        - msg:str --> the message to post on the chat"""
        self.connexion.send(f"\x0d\x00{bytes(msg)}".encode())


########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
class NeoWorld(object):
    def __init__(self, name, level=-1):
        """Args:
        - name: the name of the world (str). Used to load and save worlds.
        - level: the type of the world (int). Can be 0 (overworld), 1 (nether) or 2 (end). -1 by default. -1 is for unknow level (when loading for example)"""
        self.name = name
        if level == -1:
            self.level = None
        else:
            self.level = level
        self.loaded = False
        self.generated = None
        self.BASE = f"{os.getcwd()}{SEP}worlds{SEP}{name}{SEP}"
        self.data = None
        self.spawn_coord = None

    def load(self):
        """Load the world"""
        nbt_file = nbtlib.load(self.BASE + "level.dat")
        self.difficulty = nbt_file["Data"]["Difficulty"]
        self.wonderingtraderspawnchance = nbt_file["Data"]["WanderingTraderSpawnChance"]
        print(nbt_file)





















class World(object):
    """World class"""
    def __init__(self, name, level=-1):
        """Args:
        - name: the name of the world (str). Used to load and save worlds.
        - level: the type of the world (int). Can be 0 (overworld), 1 (nether) or 2 (end). -1 by default. -1 is for unknow level (when loading for example)"""
        self.name = name
        if level == -1:
            self.level = None
        self.level = level
        self.loaded = False
        self.generated = None
        self.BASE = "worlds/"
        self.data = None
        self.spawn_coord = None

    def check_generation(self):
        """Check if the world was generated.
        Return a boolean"""
        try:
            with open(self.BASE + self.name + ".mcworld", "r") as test:
                tst = test.read()
                if tst != "":
                    return True
                else:
                    return False
        except FileNotFoundError:
            return False
        
    def generate(self, level, force=False):
        """Generate the world.
        Args:
        - force: (bool) """
        if force:
            ok = True
        else:
            if self.data != None:
                ok = False
            else:
                ok = True
        if ok:
            self.level = level
            c1 = self._new_chunk(0, 0, 0)
            c2 = self._new_chunk(1, 0, 0)
            c3 = self._new_chunk(0, 0, 1)
            c4 = self._new_chunk(1, 0, 1)
            self.data.append(c1)
            self.data.append(c2)
            self.data.append(c3)
            self.data.append(c4)
            self.spawn_coord = {"x": 8, "y": 8, "y": 8}

    def setblock(self, x:int, y:int, z:int, id:int, nbt:str=""):
        """Modify a block into the world.
        Args:
        - x (int): the x coordinate of the block
        - y (int): the y coordinate of the block
        - z (int): the z coordinate of the block
        - id (int): the block type (see world_format.md)
        - nbt (str, "" by default): the nbt data of the block."""
        block_chunk = self._block_to_chunk_coords(x, y, z)
        chunk_index = self.data.find_chunk_index(block_chunk["x"], block_chunk["y"], block_chunk["z"], )
        chunk = self.data[chunk_index]

        bx = x % 16
        by = y % 16
        bz = z % 16
        
        size_x = 16
        size_y = 16
        size_z = 16
        x_coord = bx
        y_coord = by
        z_coord = bz

        for x in range(size_x):
            for y in range(size_y):
                for z in range(size_z):
                    index = x + size_x * (y + size_y * z)

                    element = chunk[index]

        index_cible = x_coord + size_x * (y_coord + size_y * z_coord)
        element_cible = chunk[index_cible]


    def find_chunk_index(self, x, y, z):
        """Return the chunk Index with the gived coords."""
        index = None
        for i, j in enumerate(self.data):
            if i == 0:
                continue
            if i[0]["x"] == x and i[0]["y"] == y and i[0]["z"] == z:
                index = i
                break
        return i


    def _block_to_chunk_coords(self, x:int, y:int, z:int):
        """Convert a block coord to a chunk coord. Args: the coordinates. Return the chunk coords."""
        nx = x // 16
        ny = y // 16
        nz = z // 16

        return {"x": nx, "y": ny, "z": nz}
            

    def _new_chunk(self, x:int, y:int, z:int):
        """Create a new chunk at the specified CHUNKS COORD !
        - Args:
            - x (int) the X chunk pos
            - y (int) the X chunk pos
            - z (int) the X chunk pos
        - Return the chunk (lst)"""
        c = [{"x":x, "y":y, "z":z}]
        count = 0
        while count != (16**3):
            c.append((0, ""))
        return c


    def load(self):
        """Read a world file and return a World List.
        Return data with the correct python server convention."""
        if not(self.check_generation):
            log("Trying to load an ungenerated world ! Please generate it before loading !Starting generation...", 2)
            self.generate()
        with open(self.BASE + self.name, "r") as file:
            data = file.read()
            self.decode(data)
            self.data = data
            return self.data


    def decode(self, data:str):
        """Decode some data.
        --> Return the world (see world/world_format.md## World format (in running app))"""
        infos, world = data.split("=====")
        #treat infos
        name, level = infos.split("::::")
        if name != self.name:
            #something went wrong
            log("Reading a world name different of the gived name !", 2)
            self.name = name
            log("Name modified.", 0)
        if self.level != level and self.level != None:
            #something went wrong
            log("Reading a world level different of the gived level !", 2)
            self.level = level
            log("Level modified.", 0)
        if self.level == None:
            self.level = level
        
        chunks_list = world.split("<<|<<")
        final = []
        #treat all chunks
        for chunk in chunks_list:
            base_chunk_list = []
            xyz, blocks_list = chunk.split("|")

            #Treat chunk coords
            xyz = xyz.split(";")
            chunk_coord = {"x": xyz[0], "y": xyz[1], "z": xyz[1]}
            base_chunk_list.append(chunk_coord)

            #Treat blocks
            lst_blocks = blocks_list.split(";")
            for block in lst_blocks:
                b_type, nbt = block.split(">")
                base_chunk_list.append((b_type, nbt))

            final.append(base_chunk_list)

        return final
    
    def save(self):
        """Save the world"""
        log(f"Saving world {self.name} (level {self.level})...")
        dt = self.encode(self.data)
        with open(self.BASE + self.name + ".mcworld", "w") as file:
            file.write(dt)
        log("Saved !")

    def encode(self, data:list):
        """Encode the world that will be saved.
        Arg:
        - data: (list) the data to encode.
        Return the world encoded (str)"""
        final = f"{self.name}::::{self.level}====="

        for chunk in data:
            coord_dico = chunk[0]
            final += f"{coord_dico['x']};{coord_dico['y']};{coord_dico['e']}|"

            list_blocks = chunk[1]
            for block in list_blocks:
                b_type = block[0]
                nbt = block[1]
                final += f"{b_type}>{nbt};"
            final = final[:-1]
            final += "<<|<<"

        final = final[:-5]
        
        return final


    def generate(self):
        ...


########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
class Translation(object):
    def __init__(self, lang):
        self.lang = lang

    
    def en(self, key):
        """English translation"""
        dico = {"disconnect.default": "Disconnected.", 
                "disconnect.server_full": "Server full.",
                "disconnect.not_premium": "Auth failed : user not premium.", 
                "disconnect.bad_protocol": "Please to connect with an other version : protocol not compatible.", 
                "disconnect.server_closed": "Server closed.", 
                "disconnect.server_crashed": "Server crashed indeed of a critical error."}
        return dico[key]
    
    def fr(self, key):
        """French translation"""
        dico = {"disconnect.default": "Déconnecté", 
                "disconnect.server_full": "Le serveur est plein.",
                "disconnect.not_premium": "L'authentification a échouée : utilisateur non premium.", 
                "disconnect.bad_protocol": "Merci de se connecter avec une autre version : protocole incompatioble.", 
                "disconnect.server_closed": "Serveur fermé.", 
                "disconnect.server_crashed": "Le serveur a planté suite à une erreur critique."}
        return dico[key]
    
    def es(self, key):
        """Espagnol translation"""      #TODO
        dico = {"disconnect.default": "Disconnected.", 
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
        elif self.lang == "fr":
            return self.fr(key)
        elif self.lang == "es":
            log("This lang is not translated !", 1)
            return self.es(key)
        else:
            log("Lang not found !", 100)
            exit(-1)


########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
#Exception class
class RequestAnalyseException(Exception):
    """Exception when analysing a request"""
    pass

class TwoPlayerWithSameUsernameException(Exception):
    """Exception when 2 players or more have the same username"""

class Command(object):
    def __init__(self, command:str, source:Client, server:MCServer):
        self.COMMANDS = {"/msg": self.msg, 
                "/tell": self.msg, 
                "/stop":self.stop}   #other will be added later

        self.srv = server

        self.command = command
        self.source = source
        self.splited = self.command.split(" ")
        self.base = self.splited[0]
        self.args = self.splited[1:]

        if self.pre_cmd():
            self.execute()
        else:
            self.__del__()

    def execute(self):
        cmdf = self.COMMANDS[self.base]
        if cmdf():
            ...#ok
        else:
            ...#error


    def check_perm(self):
        #if self.base in self.source.perms:
        #   return True
        #else:
        #   return False
        return True

    def pre_cmd(self):
        log(f"{self.source.username} used a player command : {self.command}.", 4)
        if self.check_perm(self.base, self.source):
            return True
        else:
            log(f"Denied acces for the command {self.base} runned by {self.source.username} !", 4)
            return False

    def msg(self, args):
        player = args[0]
        msg = args[1:]
        self.srv.mp(msg, player, self.source.username)
        return True
    
    def stop(self, args):
        if len(args) != 0:
            log("Too much arguments !", 1)
            self.srv.mp("Too many arguments !", self.source, )
            return False
        self.srv.stop()
        return True

#PRE MAIN INSTRUCTIONS
be_ready_to_log()


#MAIN
if __name__ == "__main__":
    try:
        log('Starting Plugin APi', 3)
        pluginapi.init_api()
        tr = Translation(lang)
        srv = MCServer()
        srv.start()
    except Exception as e:
        log("FATAL ERROR : An error occured while running the server : uncaught exception.", 100)
        log(f"{type(e)}: {e}", 100)
        srv.stop(critical=True, reason=f"{type(e)}: {e}")

