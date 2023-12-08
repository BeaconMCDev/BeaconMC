"""A plugin example for BeaconMC"""

import plugins.example.pluginsystem as plsys

class Plugin(plsys.BeaconMCPlugin):
    def __init__(self, server:object=None):
          super().__init__(name="ExamplePlugin", author="FewerElk", version="1.0", srv_version="Alpha-dev", server=server)

    def on_load(self):
         self.server.log(f"Loading {self.name} from {self.author} (v {self.version})... COMPLETE !", 0)

    def on_unload(self):
         self.server.log(f"Goodbye !", 0)

    def on_player_death(self, player: str, message: str):
         self.server.mp("Don't worry... You will not loose the next time ! (I hope :-))", player)