from entity import Entity

class LivingEntity(Entity):
    def __init__(self, namespace, name, id, uuid, location=None, attributes={}):
        super().__init__(namespace, name, id, uuid, location)
        self._attributes = attributes
        self._health = attributes.get("max_health", 20)
        
    @property
    def attributes(self):
        return self._attributes
        
    @attributes.setter
    def attributes(self, value:tuple):
        if not(isinstance(value, tuple) and len(value == 2)):
            raise ValueError
        
        self._attributes[value[0]] = value[1]
        
    def damage(self, damages:int):
        if not(isinstance(damages, int)):
            raise TypeError("Damage must be an integer")
        
        if damages <= 0:
            raise ValueError("Damage must be positive")
        
        self._health -= damages
        if self._health < 0:
            self._health = 0
            self.kill()

    def heal(self, amount:int):
        if not(isinstance(amount, int)):
            raise TypeError("Heal amount must be an integer")
        if amount <= 0:
            raise ValueError("Heal amount must be positive")
        
        self._health += amount
        if self._health > self._attributes.get("max_health", 20):
            self._health = self._attributes.get("max_health", 20)

    def kill(self):
        self._health = 0
        ...