class BeaconMCPlugin(object):
    def __str__(cls, server):
        cls.server = server
        return cls
      
    def __init__(self, server):
        self.server = server
        for name in dir(self):
            method = getattr(self, name)
            if hasattr(method, "_mc_event"):
                # register
                # self.server.register(method._mc_event, method)

    def onEnable(self):
      pass

    def onDisable(self):
        pass

    def onPlayerJoinEvent(self, player):
        pass
    