class Registry(object):
    def __init__(self, namespace:str, name:str, base_ptn:dict):
        self.namespace = namespace
        self.name = name
        self.displayName = f"{namespace}:{name}"
        self._BASE_PTN = base_ptn
        ...
        
    def get_entity_name(id:int):
        return self._BASE_PTN[id]
        