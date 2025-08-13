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
        11: "bee",
        12: "birch_boat",
        13: "birch_chest_boat",
        14: "blaze",
        15: "block_display",
        16: "bogged",
        17: "breeze",
        18: "breeze_wind_charge",
        19: "camel",
        20: "cat",
        21: "cave_spider",
        22: "cherry_boat",
        23: "cherry_chest_boat",
        24: "chest_minecart",
        25: "chicken",
        26: "cod"
        27: "command_block_minecart",
        28: "cow",
        29: "creaking",
        30: "creeper",
        31: "dark_oak_boat",
        32: "dark_oak_chest_boat",
        33: "dolphin",
        34: "donkey",
        35: "dragon_fireball",
        36: "drowned",
        37: "egg",
        38: "elder_guardian",
        39: "enderman",
        40: "endermite",
        41: "ender_dragon",
        42: "ender_pearl",
        43: "end_crystal",
        44: "evoker",
        45: "evoker_fangs",
        46: "experience_bottle",
        47: "experience_orb", # DO NOT SPAWN WITH ˋSPAWN ENTITY` PACKET
        48: "eye_of_ender",
        49: "falling_block",
        50: "fireball",
        51: "firework_rocket",
        52: "fox",
        53: "frog",
        54: "furnace_minecart",
        55: "ghast",
        56: "happy_ghast",
        57: "giant",
        58: "glow_item_frame",
        59: "glow_squid",
        60: "goat"
    }
    ...
    
    def __init__(self):
        super().__init__("minecraft", "entities", self._BASE_PTN)
    