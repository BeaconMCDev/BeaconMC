import registry.py as regist

class EntitiesRegistry(regist.Registry):
    
    # The base registry used to convert protocol ids to names and classes
    _BASE_PTN = {
        0: "acacia_boat",
        1: "acacia_chest_boat",
        2: "allay",
        3: "area_effect_cloud",
        4: "armadillo",
        5: "armor_stand",
        6: "arrow",
        7: "axolotl",
        8: "bamboo_chest_raft",
        9: "bamboo_raft",
        10: "bat",
        11: "bee"
    }
    ...
    
    def __init__(self):
        super().__init__("minecraft", "entities", self._BASE_PTN)
    