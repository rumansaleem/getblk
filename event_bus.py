from threading import Event

class EventBus:
    EVENT_WAIT_ANY_BUFFER = "wait:buffer"
    EVENT_WAIT_SPECIFIC_BUFFER = lambda buf: f"wait:buffer.{buf}"

    def __init__(self):
        self.events = {}
    
    def sleep(self, eventName):
        if eventName in self.events:
            self.events[eventName].wait()
        else:
            self.events[eventName] = Event()
            self.events[eventName].wait()

    def wake(self, eventName):
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