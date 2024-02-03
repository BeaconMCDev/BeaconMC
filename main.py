"""Minecraft server in python 3.11
Sources for dev : 
- https://minecraft.fandom.com/wiki/Classic_server_protocol
- https://minecraft.fandom.com/wiki/Protocol_version?so=search"""

print("_________________________________________________________\nStarting Minecraft server in Python 3.11\n_________________________________________________________")

print("Importing librairies...")
#IMPORTS - LIBRAIRIES
import socket as skt
import tkinter as tk
from tkinter.simpledialog import *
import time as tm
import random as rdm
import os
import threading as thread
import hashlib #for md5 auth system
import platform
import pluginapi
import json

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
        elif dt[0] == "max_players":
            MAX_PLAYERS = int(arg)
        elif dt[0] == "motd":
            MOTD = arg
        elif dt[0] == "debug_mode":
            dico = {"true": True, "false": False}
            DEBUG = dico[arg]
        elif dt[0] == "lang":
            lang = dt[1]
        else:
            continue

print("Setting up the server...")
print("OS compatibility checking...")
COMPATIBLE_OS = ["Windows", "Linux"]
OS = platform.system()
if OS in COMPATIBLE_OS:
    if OS == "Linux":
        SEP = '/'
    elif OS == "Windows":
        SEP = "\\"
else:
    raise RuntimeError(f"OS {OS} is not compatible ! Please use Linux or Windows !")
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
    elif type == 4:
        t = "CHAT"
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
    print("Log system ready !")

def encode(msg:str):
    """Convert quickly a string into bytes that will be sended to the client."""
    return bytes(msg)
    
    
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
#CLASSES
class MCServer(object):
    """Minecraft server class"""

    SERVER_VERSION = "Alpha-dev"
    CLIENT_VERSION = "1.16.5"   
    PROTOCOL_VERSION = 754      
    PORT = 25565                
    IP = "0.0.0.0"

    def __init__(self):
        """Init the server"""
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)  #socket creation
        self.socket.bind((IP, PORT))            #bind the socket
        self.list_info = []
        self.list_clients = []
        self.list_worlds = []

    def worlds_analyse(self):
        """Search for worlds in the worlds folder.
        Return a list str that are the world name."""
        log("Analysing worlds...", 3)
        items_list = os.listdir(f"{os.getcwd()}{SEP}worlds")
        lst_world = []
        for item in items_list:
            name, extention = item.split(".")
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
        self.main()

    def load_plugins(self):
        """Load the plugins"""
        import plugins.modulable_pluginsystem as mplsys
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
        log("DONE !", 0)

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
            self.client_id_count += 1
            tm.sleep(0.1)
        
    def heartbeat(self):
        """# DEPRECATED - DO NOT USE
        Heartbeat to mojangs servers. See https://minecraft.fandom.com/wiki/Classic_server_protocol#Heartbeats for details"""
        raise DeprecationWarning("We actually have an issue for this method. It does not work.")
        global public
        dico = {True: "true", False: "false"}
        request = f"POST /heartbeat.jsp?port={PORT}&max={MAX_PLAYERS}&name={MOTD}&public={dico[public]}&version={PROTOCOL_VERSION}&salt={SALT}&users={connected_players}\r\n"
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


########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
class Client(object):
    def __init__(self, connexion, info, server:MCServer):
        log("New client", 3)
        self.connexion = connexion
        self.info = info
        self.server = server
        self.is_op = False
        self.x = None
        self.y = None
        self.z = None
        self.connected = True

    def client_thread(self, id):
        """Per client thread"""
        self.id = id
        while self.connected:
            try:
                self.request = self.connexion.recv(4096)
                self.connexion.send(b'\x85\x01\x00\x82\x01{"version":{"name":"1.16.5","protocol":754},"players":{"max":0,"online":0,"sample":[]},"description":{"text":"{\"health\":true}"}}')

            except:
                continue
            if self.request == "":
                continue
            log(self.request, 3)

            if self.request == b'\x10\x00\xf2\x05\t127.0.0.1c\xdd\x01\x01\x00':
                self.connexion.send(b'\x85\x01\x00\x82\x01{"version":{"name":"1.16.5","protocol":754},"players":{"max":0,"online":0,"sample":[]},"description":{"text":"{\"health\":true}"}}')
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

    def bad_version(self):
        """Called to disconnect the connecting client that has a bad protocol version"""
        self.connexion.send(b'E\x00C{"translate":"multiplayer.disconnect.incompatible","with":["{0}"]}'.format(SERVER_VERSION))
        self.connected = False
        self.connexion.close()
        self.server.list_client.remove(self)

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
                    log(f"Failed to connect {self.username} : bad version.", 0)
                    #self.disconnect(tr.key("disconnect.bad_protocol"))   :-(
                    self.bad_version()
            else:
                log(f"Failed to connect {self.username} : server full.", 1)
                self.disconnect(tr.key("disconnect.server_full"))
        else:
            log(f"User {self.username} is not premium ! Access couldn't be gived.", 1)
            self.disconnect(tr.key("disconnect.not_premium"))

    def disconnect(self, reason=""):
        """Disconnect the player
        !!! not disconnectED !!!"""
        self.connected = False
        if reason == "":
            reason = tr.key("disconnect.default")
        self.connexion.send(f"\x0e{bytes(reason)}".encode())
        self.connexion.close()
        self.server.list_client.remove(self)
        del(self)

    def do_spawn(self):
        """Make THIS CLIENT spawn"""
        ...
        #self.connexion.send()

    def identification(self):
        """Send id packet to the client"""
        opdico = {True:bytes("\x64"), False: bytes("\x00")}
        self.connexion.send(f"\x00{bytes(PROTOCOL_VERSION)}{bytes('Python Server 1.16.5')}{bytes(MOTD)}{opdico[self.is_op]}".encode())

    def ping(self):
        """Ping sent to clients periodically."""
        self.connexion.send("\x01".encode())
    def SLP(self, msg: str):
        log("Received ping", 3)
        if msg == "\x01":  # Check for SLP packet ID
            response = {
                "version": {"name": f"{SERVER_VERSION}", f"protocol": {PROTOCOL_VERSION}},
                "players": {"max": 100, "online": 0, "sample": [{"name": "thinkofdeath", "id": "4566e69f-c907-48ee-8d71-d7ba5aa00d20"}]},
                "description": {"text": "Hello world"},
                "favicon": "data:image/png;base64,<data>",
                "enforcesSecureChat": True,
                "previewsChat": True
            }   #I think that is the older slp ever.

            response_str = json.dumps(response)
            response_length = str(len(response_str))
            packet = f"\x01{response_length}{response_str}"
            self.connexion.send(packet.encode())

    def on_SLP(self):
        log("Event 'on server list ping' triggered !", 3)
        request = f'\xca\x01\x00\xc7\x01{"previewsChat":false,"description":{"text":"{MOTD}"},"players":{"max":{MAX_PLAYERS},"online":{len(self.server.list_clients)}},"version":{"name":"1.19","protocol":759}}'


            #self.connexion.send(f'0x01{"version":{"name":"1.19.4","protocol":762},"players":{"max":100,"online":5,"sample":[{"name":"thinkofdeath","id":"4566e69f-c907-48ee-8d71-d7ba5aa00d20"}]},"description":{"text":"Hello world"},"favicon":"data:image/png;base64,<data>","enforcesSecureChat":true,"previewsChat":true}')
    def send_msg_to_chat(self, msg:str):
        """Post a message in the player's chat.
        Argument:
        - msg:str --> the message to post on the chat"""
        self.connexion.send(f"\x0d\x00{bytes(msg)}".encode())


########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
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
        log("FATAL ERROR : An error occured while running the server : uncatched exception.", 100)
        log(e, 100)
        srv.crash(e)

