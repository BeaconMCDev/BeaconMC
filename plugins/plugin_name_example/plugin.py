""" BeaconMC example plugin for the new system
You should use this template for every plugin to avoid potential bugs or damages."""

# Import plugin class parent
from utils.plugins.BeaconMCPlugin import BeaconMCPlugin

# First, the plugin file MUST contain the Plugin class
class Plugin(BeaconMCPlugin):

    # Here place the plugin properties (equivalent of plugin.yml file in Java plugins)

    # Name of the plugin
    NAME = "Plugin name"

    # Author if only one
    AUTHOR = "FewerElk"
    # If there are most than one author use
    # AUTHORS = ("FewerElk", "Sunwaterdev")

    # Version
    VERSION = "1.0"
    
    # Don't touch, they are misc variables
    _loaded = False
    _disabled = False
    
    server = None


    def __init__(self, server):
        """Get the server instance from the loader.
        MUST BE WRITTEN"""
        super().__init__(server)

    # Note : all the following events method are optinnal but you have to respect the arguments
    def onEnable(self):
        """Similar to Java plugins"""
        # In this exemple the plugin will log into the console "Hello World"
        self.server.getConsole().log("Hello World", 0)

    def onDisable(self):
        self.server.getConsole().log("GoodBye !", 0)

    @server.EventHandler("playerJoinEvent")
    def onPlayerJoinEvent(self, player):
        self.server.post_to_chat(f"Welcome {player.username} !")