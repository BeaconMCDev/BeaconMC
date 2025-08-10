class Registry(object):
    def __init__(self, namespace:str, name:str):
        self.namespace = namespace
        self.name = name
        self.displayName = f"{namespace}:{name}"
        