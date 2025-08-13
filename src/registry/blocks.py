import registry

class BlocksRegistry(registry.Registry):
    _BASE_PTN = {
        ... # i need to find the correct source
    }
    
    def __init__(self):
        super().__init__("minecraft", "blocks", self._BASE_PTN)