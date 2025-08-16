class BeaconMCPlugin(object):
    def __str__(cls, server):
        cls.server = server
        return cls
      
    def __init__(self, server):
        self.server = server
        self._loaded = False
        self._enabled = False
        
    def onEnable(self):
      pass

    def onDisable(self):
        pass

    def onPlayerJoinEvent(self, player):
        pass
    