class EventManager(object):
    """The class for event-related management (server and plugins)"""
    
    def __init__(self, server):
        self._server = server
        self._events = {"playerJoinEvent": []}
        
    def register(self, plugin, event, wrapper):
        event_list = self._events[event]
        event_list.append((plugin, wrapper))