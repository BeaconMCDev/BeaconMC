"""The plugin api that allow plugin creation"""

#class
class Plugin(object):
    def __init__(self, name:str, author:str, server:object, version:str, srv_version:str):
        self.name = name
        self.author = author
        self.server = server
        self.version = version
        self.srv_version = srv_version

        #NOTE ABOUT THE STATE ATTRIBUTE : 0 is not loaded, 1 is loaded, -1 is disabled (suite of an error or a server stop)
        self.state = 0

    # Plugin.on_load() and Plugin.on_unload() are not here, and have to be included in the plugin created by someone

    def _on_load(self):
        """# DON'T CALL IT FROM THE PLUGIN - FOR SERVER MISC ONLY
        ### --> DON'T TOUCH !!!"""
        self.server.log(f"Loading the plugin {self.name} from {self.author} (v{self.version})...", 0)
        if self.srv_version == self.server.SERVER_VERSION:
            self.server.log(f"COMPLETE !", 0)
            self.state = 1
        else:
            self.server.log(f"Bad server version for the plugin {self.name} !", 1)
            self.disable()

    def disable(self):
        self.state = -1
        self.LOCK = True   #used to block the bypasses

    def on_player_join(self, player:str):
        pass

    def on_player_leave(self, player:str):
        pass

    def on_player_death(self, player:str, message:str):
        pass

    def on_player_reaspawn(self, player:str):
        pass

    def on_message(self, messag:str, sourcev):
        pass

    def on_mp(self, message:str, source:str, addressee:str):
        pass