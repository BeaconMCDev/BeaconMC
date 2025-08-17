class Event:
    def __init__(self, event:str):
        self._eventType = event
        self._cancelled = False
        
    @property
    def cancelled(self):
        return self._cancelled
        
    @_cancelled.setter
    def cancelled(self, value):
        if not(value):
            raise ValueError("You can't uncancel an event.")
        self._cancelled = True
        
    def cancel(self):
        self.cancelled = True
