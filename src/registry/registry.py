class Registry(object):
    def __init__(self, namespace:str, name:str, base_ptn:dict):
        self.namespace = namespace
        self.name = name
        self.displayName = f"{namespace}:{name}"
        self._BASE_PTN = base_ptn
        self._BASE_NTP = {v: k for k, v in base_ptn.items()}
        
    def get_entity_name(self, id:int):
        return self._BASE_PTN[id]
        
    def get_entity_protocol_id(self, name:str):
        return self._BASE_NTP[name]