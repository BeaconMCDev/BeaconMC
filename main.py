""" BeaconMC - Python 3
    Source for dev :
    - https://wiki.vg"""

# IMPORTS - LIBRAIRIES
import math
import socket as skt
import time as tm
import random as rdm
import plugins.modulable_pluginsystem as mplsys
from typing import Literal
import threading as thread
import os
import hashlib  # for md5 auth system
import platform
import pluginapi
import json
import mojangapi as m_api
import struct
import uuid
import traceback
try:
    import nbtlib
except ModuleNotFoundError:
    print("Installing missing library...")
    os.system("pip install nbtlib")
    import nbtlib
    print("Done")

print("_________________________________________________________\nStarting BeaconMC 1.19.4\n_________________________________________________________")

dt_starting_to_start = tm.time()
lthr = []


# BASE ERROR
class OSNotCompatibleError(OSError):
    pass


# CONFIG READING
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
            dico = {"true": False, "false": True}
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

# GLOBAL DATAS - VARIABLES
connected_players = 0
blacklist = []
whitelist = []
# public = True
users = []
logfile = ""
state = "OFF"

# GLOBAL DATAS - CONSTANTS
# ################################
# ##          READ THIS       ####
# ## don't touch this section ####
# ################################

SERVER_VERSION = "Alpha-dev"    # Version of the server. For debug
CLIENT_VERSION = "1.19.4"       # Which version the client must have to connect
PROTOCOL_VERSION = 762          # Protocol version beetween server and client. See https://minecraft.fandom.com/wiki/Protocol_version?so=search for details.
PORT = 25565                    # Normal MC port
IP = "0.0.0.0"
# MAX_PLAYERS = 5
SALT_CHAR = "a-z-e-r-t-y-u-i-o-p-q-s-d-f-g-h-j-k-l-m-w-x-c-v-b-n-A-Z-E-R-T-Y-U-I-O-P-Q-S-D-F-G-H-J-K-L-M-W-X-C-V-B-N-0-1-2-3-4-5-6-7-8-9".split("-")
SALT = ''.join(rdm.choice(SALT_CHAR) for i in range(15))
CONFIG_TO_REQUEST = {"\u00A7": "\xc2\xa7", "§": "\xc2\xa7"}
# log counts
errors = 0
warnings = 0
debug = 0
info = 0
critical = 0
unknow = 0

print("")


def log(msg: str, type: int = -1):
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
        if not (DEBUG):
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
    try:
        with open(logfile, "+a") as file:
            file.write(text + "\n")
    except Exception:
        print('Error in log system! Creating file... ')
        os.mkdir('logs')
        with open(logfile, "+w") as file:
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


def encode(msg: str):
    """Convert quickly a string into bytes that will be sended to the client."""
    return msg.encode()


# #######################################################################################################################################################################################################################
# #######################################################################################################################################################################################################################
# #######################################################################################################################################################################################################################
# CLASSES
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
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)  # socket creation
        self.socket.bind((IP, PORT))            # bind the socket
        self.list_info = []
        self.list_clients = []
        self.list_worlds = []
        try:
            with open("eula.txt", "r") as eula_file:
                eula = eula_file.read().split()
                if "eula=true" in eula:
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
            self.stop(False, reason="You need to agree eula to continue.")
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

    def log(self, msg: str, type: int = -1):
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
        # self.heartbeat()

        log("Loading plugins...", 0)
        self.load_plugins()

        log("Starting console GUI...", 0)
        self.gui = ConsoleGUI()

        self.gui_thr = thread.Thread(target=self.gui.mainthread)
        self.gui_thr.start()
        lthr.append(self.gui_thr)

        log("Starting listening...", 0)
        self.socket.listen(MAX_PLAYERS + 1)  #+1 is for the temp connexions

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

    def stop(self, critical_stop=False, reason="Server closed", e:Exception=None):
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
            self.crash(reason, e)
            exit(-1)


    def crash(self, reason, e:Exception=None):
        """Generate a crash report
        Arg:
        - reason: str --> The crash message"""
        c = 0
        try:
            import datetime
            t = traceback.format_exc()
        except:
            t = None
        while os.path.exists("crash_reports/crash{0}".format(c)):
            c += 1
        with open("crash_reports/crash{0}".format(c), "w") as crashfile:
            crashfile.write(f"""{datetime.datetime.now()}\nBeaconMC {SERVER_VERSION}\nFor Minecraft {CLIENT_VERSION}\n________________________________________________________________________________________________________________\nCritical error, the server had to stop. This crash report contain informations about the crash.\n________________________________________________________________________________________________________________\nCause of the crash : {reason}\n{traceback.format_exc(e)}\nDebug mode : {DEBUG}\n________________________________________________________________________________________________________________\n{t}""")


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
            #self.list_clients.append(cl)
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
            msg = f"<{author}>: {message}"
        for p in self.list_clients:
            p: Client
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
        self.unpack()

    def unpack_uuid(self, uuid):
        if len(uuid) != 16:
            raise ValueError(f"invalid lenth {len(uuid)} for binary uuid")

        hex_uuid = uuid.hex()
        uuid_format = f"{hex_uuid[:8]}-{hex_uuid[8:12]}-{hex_uuid[12:16]}-{hex_uuid[16:20]}-{hex_uuid[20:]}"

        return uuid_format

    def wait_for_packet(self):
        if self.type == "-INCOMING":
            self.lenth = self.unpack_varint(self.socket.recv(1))
            tc = self.lenth
            if self.lenth <= 0:
                raise PacketException("NullPacket")
            self.id = self.unpack_varint(self.socket.recv(1))
            tc -= 1
            if self.id == 0:
                # 2 more possibles cases
                ...
        else:
            raise PacketException("Wating to receive packet in -OUTGOING mode")

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
    
    def unpack_varint(data):
        d = 0
        for i in range(5):
            b = data[i]
            d |= (b & 0x7F) << (7 * i)
            if not b & 0x80:
                break
        return d
    
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
            if isinstance(i, int):
                out += self.pack_varint(len(self.pack_varint(i))) + self.pack_varint(i)
            elif isinstance(i, UUID):
                out += (self.pack_varint(1) + self.pack_uuid(i))
            elif isinstance(i, bool):
                if i:
                    out += b"\x01"
                else:
                    out += b"\x00"
            elif isinstance(i, tuple):
                ...
            else:
                out += self.pack_data(i)
        out = self.pack_varint(len(out)) + out
        return out
    
    def pack_uuid(self, uuidObject):
        uuid = uuidObject.uuid

        hex_uuid = uuid.replace('-', '')

        binaire_uuid = bytes.fromhex(hex_uuid)

        return binaire_uuid
    
    def __str__(self):
        return self.__repr__().decode()

########################################################################################################################################################################################################################
########################################################################################################################################################################################################################
########################################################################################################################################################################################################################

class UUID(object):
    def __init__(self, uuid):
        self.uuid = uuid

class Client(object):
    def __init__(self, connexion: skt.socket, info, server:MCServer):
        self.connexion = connexion
        self.info = info
        self.server = server
        self.is_op = False
        self.x = None
        self.y = None
        self.z = None
        self.connected = True
        self.protocol_state = "Handshaking"

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
            log(f"New client from {self.info}", 3)
            log("Starting listening loop in Handshaking state", 3)

            # Ping / Auth loop (to developp)
            d_reason = "None"
            misc_d = True
            while self.connected and state == "ON":
                # Auth loop
                try:
                    lenth = self.connexion.recv(1)
                    self.request = lenth + self.connexion.recv(Packet.unpack_varint(lenth))
                except ConnectionResetError:
                    log(f"Client {self.info} disconnected : Connexion reset.")
                if self.request == "":
                    continue
                log(self.request, 3)

                self.packet = Packet(self.connexion, "-INCOMING", packet=self.request)

                if self.packet.type == 0 and self.protocol_state == "Handshaking":
                    #Handshake

                    if self.packet.args[-1] == 1:
                        # Switch protocol state to status
                        self.protocol_state = "Status"
                        log(f"Switching to Status state for {self.info}", 3)

                        continue

                    elif self.packet.args[-1] == 2:
                        # Switch protocol state to login
                        self.protocol_state = "Login"
                        log(f"Switching to login state for {self.info}", 3)

                        continue

                    elif self.packet.args[-1] == 3:
                        # Switch protocol state to transfer
                        self.protocol_state = "Transfer"
                        log(f"Switching to transfer state for {self.info}", 3)
                        
                        continue
                    else:
                         self.connected = False
                         self.connected = False
                         log(f"Disconnecting {self.info} : protocol error (unknow next state {self.packet.args[-1]} in handshake)", 3)
                         break

                elif self.packet.type == 0 and self.protocol_state == "Status":
                    #Status request -> Status response (SLP)
                    self.SLP()
                    continue

                elif self.packet.type == 0 and self.protocol_state == "Login":

                    unamelenth = self.packet.args[0]
                    i = 1
                    self.username = ""
                    while i <= unamelenth:
                        sb = self.packet.args[i:i+1]
                        self.username += sb.decode("utf-8")
                        i += 1

                    self.uuid = self.packet.unpack_uuid(uuid=self.packet.args[i+1:])

                    log(f"UUID of {self.username} is {self.uuid}.", 0)
                    log(f"{self.username} is logging in from {self.info}.", 0)

                    if len(self.server.list_clients) >= MAX_PLAYERS:

                        self.connected = False
                        misc_d = False
                        d_reason = "Server full"
                        continue
                    if not(public):
                        with open("whitelist.json", "r") as wf:
                            data = json.loads(wf.read())
                            o = 0
                            for d in data:
                                if d["uuid"] == self.uuid:
                                    o += 1
                            if o != 1:
                                self.connected = False
                                
                                d_reason = "You are not whitelisted on this server."
                                misc_d = False
                    
                                if o > 1:
                                    log("User is whitelisted more than 1 time !", 1)
                                continue
                    if ONLINE_MODE:
                        #TODO Encryption Request
                        ...
                    
                        api_system = m_api.Accounts()
                        check_result = api_system.authenticate(self.username, self.uuid)
                        if check_result[0]:
                            log(f"sucessfully authenticated {self.username}.", 3)
                            pass
                        else:
                            log(f"Failed to authenticate {self.info} using uuid {self.uuid} and username {self.username}.", 1)
                            self.connected = False
                            d_reason = "Failed to login"
                            misc_d = False
                        
                        #TODO Enable compression (would be optional) (in other "if" fork)
                        ...
                    else:
                        #load player properties
                        ...
                        self.properties = ()
                        response = Packet(self.connexion, "-OUTGOING", 2, args=(UUID(self.uuid), self.username, 0, not(DEBUG)))
                        log(response.__repr__(), 3)
                        response.send()
                        self.server.list_clients.append(self)
                        break

                elif self.packet.type == 1 and self.protocol_state == "Status":
                    payload = self.packet.args[0]
                    self.ping_response(payload)
                    self.connected = False
                    break

            ###############################################################################


            if not(self.connected and state == "ON"):
                #If server is stopping or the client is disconnecting (usefull ?)
                if misc_d:
                    log(f"Disconnecting {self.info} for some misc reasons.", 3)
                else:
                    dp = Packet(self.connexion, "-OUTGOING", typep=27, args=(f'\{"text":"{d_reason}"\}', ))
                    log(f"{self.username} lost connexion: {d_reason}.", 0)
                self.connexion.close()
                return
            
            ###############################################################################

            log(f"{self.username} joined the game.", 0)
            self.server.post_to_chat(f"{self.username} joined the game")
            while self.connected and state == "ON":
                #to clean
                

                l = self.connexion.recv(1)
                self.packet = Packet(self.connexion, "-INCOMING", packet=self.request)
                
                ...


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
        except ConnectionAbortedError:
            log(f"Connexion aborted by client {self.info} ({self.username})", 0)
            self.connexion.close()
            self.connected = False
        except Exception as e:
            import traceback
            log(f"{traceback.format_exc()}", 2)
            self.connected = False
            dp = Packet(self.connexion, "-OUTGOING", typep=27, args=('{"text":"Internal server error"}', ))

        
    def ping_response(self, payload):
        """Send a response to a ping to make the client get the ping in ms of the server."""

        response = Packet(self.connexion, "-OUTGOING", typep=1, args=(payload,))
        response.send()
        
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
            log("Server icon not found, using default BeaconMC icon", 1)
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
        packet = Packet(self.connexion, "-OUTGOING", 108, args=("{'color':'#FFDE59', 'text':'" + self.username + "joined the game.}", False))
        print(packet.__repr__())
        packet.send()


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
        #Load world settings
        nbt_file = nbtlib.load(self.BASE + "level.dat")
        self.difficulty = nbt_file["Data"]["Difficulty"]
        self.wonderingtraderspawnchance = nbt_file["Data"]["WanderingTraderSpawnChance"]
        ...

        self.regions = []
        


class Region(object):
    def __init__(self, x:int, z:int, world_name:str):
        self.x = x
        self.z = z
        self.file = f"worlds{SEP}{world_name}r.{x}.{z}.mca"

    def is_chunk_in_region(self, x:int, z:int) -> bool:
        region_xz = lambda x,z: (math.floor(x / 32), math.floor(z / 32))
        return region_xz(x, z) == (self.x, self.z)



















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
    
class ConsoleGUI(object):
    def __init__(self):
        ...

    def mainthread(self):
        ...

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
        log(f"{traceback.format_exc(e)}", 100)
        srv.stop(critical_stop=True, reason=f"{e}", e=e)

