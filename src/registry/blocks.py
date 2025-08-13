import registry

class BlocksRegistry(registry.Registry):
    _BASE_PTN = {
        0: "air"
        ... # i need to find the correct source
    }
    
    def __init__(self):
        super().__init__("minecraft", "blocks", self._BASE_PTN)