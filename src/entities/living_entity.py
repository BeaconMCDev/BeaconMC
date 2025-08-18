from entity import Entity

class LivingEntity(Entity):
    def __init__(self, namespace, name, id, uuid, location, attributes):
        super().__init__(namespace, name, id, uuid, location)
        self._attributes = attributes
        
    @property
    def attributes(self):
        return self._attributes
        
    @_attributes.setter
    def attributes(self, value:tuple):
        if not(isinstance(value, tuple) and len(value == 2) raise ValueError
        
        self._attributes[value[0]] = value[1]
        
    # def damage(self, 