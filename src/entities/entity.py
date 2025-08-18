from ..registry.entities import EntityRegistry
from ..location import Location
from ..vector import Vector

class Entity:
    REGISTRY = EntityRegistry
    
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
        
    @location.setter
    def location(self, value:Location):
        if not(isinstance(value, Location)):
            raise TypeError
        self._location = value

    def move(self, vector:Vector):
        if not(isinstance(vector, Vector)):
            raise TypeError("Vector must be an instance of Vector")
        if self._location is None:
            raise ValueError("No location set for entity")
        
        self._location = self._location.move(vector)