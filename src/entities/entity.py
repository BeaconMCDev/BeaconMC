from ..registry.entities import EntityRegistry
from ..location import Location

class Entity:
    REGISTRY = EntityRegistry()
    
    def __init__(self, namespace:str, name:str, id, uuid, location:Location=None):
        self.NAMESPACE = namespace
        self.NAME = name
        self.DISPLAYNAME = f"{namespace}:{name}"
        self.ID = id
        self.UUID = uuid
        self._location = location
        self.RGID = self.REGISTRY.getProtocolID(id)
        
    @property
    def location(self):
        if self._location == None:
            raise ValueError("No location provided")
        return self._location
        
    @_location.setter
    def location(self, value:Location):
        if not(isinstance(value, Location)):
            raise TypeError
        self._location = value

