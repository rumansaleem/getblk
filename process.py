class Process:
    def __init__(self, blockNumber, operation, ttl = 10):
        self.bufferHeader = None
        self.state = None
        self.waiting = False
        self.ttl = ttl
        self.blockNumber = blockNumber
        self.operation = operation