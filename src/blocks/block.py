from ..registry.blocks import BlockRegistry
from ..location import Location

class Block:
    REGISTRY = BlockRegistry

    def __init__(self, namespace:str, name:str, location:Location, properties={}):
        self.NAMESPACE = namespace
        self.NAME = name
        self.LOCATION = location
        self.properties = properties
        self.DISPLAYNAME = f"{namespace}:{name}" if properties == {} else f"{namespace}:{name}[{', '.join(f'{k}={v}' for k, v in properties.items())}]"
        self.RGID = self.REGISTRY.get_block_protocol_id(f"{name}" if properties == {} else f"{namespace}:{name}[{', '.join(f'{k}={v}' for k, v in properties.items())}]")
