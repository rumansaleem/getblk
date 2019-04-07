from threading import Event

"""
Events are objects that can be accesed by all threads, we use them to control when a process will sleep/wake
"""
class EventBus:
    EVENT_WAIT_ANY_BUFFER = "wait:buffer"
    EVENT_WAIT_SPECIFIC_BUFFER = lambda buffer: f"wait:buffer.{buffer.id}"

    def __init__(self):
        self.events = {}
    
    def sleep(self, eventName, createNew = True):
        """
        Sleeps the process until the 'eventName' happens
        """
        if eventName in self.events:
            self.events[eventName].wait()
        elif createNew:
            self.events[eventName] = Event()
            self.events[eventName].wait()

    def wake(self, eventName):
        """
        Wakes the process when the 'eventName' happens
        """
        if eventName in self.events:
            self.events[eventName].set()
    
    def clear(self, eventName):
        if eventName in self.events:
            self.events[eventName].clear()

        event = Event()
        event.clear()
        self.events[eventName] = event

    def isSet(self, eventName):
        if eventName in self.events:
            return self.events[eventName].isSet()
        return False

    def __repr__(self):
        return str(self.events)