""" BeaconMC example plugin for the new system
You should use this template for every plugin to avoid potential bugs or damages."""

# First, the plugin file MUST contain the Plugin class
class Plugin(object):

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


    def __init__(self, logger, server):
        """Get the server instance from the loader.
        MUST BE WRITTEN"""
        self.server = server

    # Optionnal
    def onEnable(self):
        """Similar to Java plugins"""
        # In this exemple the plugin will log into the console "Hello World"
        self.server.log("Hello World", 0)

    # Optionnal
    def onDisable(self):
        self.server.log("GoodBye !", 0)

    # Optionnal
    def onPlayerJoinEvent(self, player):
        self.server.post_to_chat(f"Welcome {player.username} !")

    # etc
