class Buffer:
    def __init__(self, id):
        self.id = id
        self.nextInHashQueue = None
        self.previousInHashQueue = None
        self.nextInFreeList = None
        self.previousInFreeList = None

        self.blockNumber = None

        # status variables
        self.data = None # data contents held in the buffer
        self.locked = False # buffer is locked/busy
        self.delayWrite = False #kernel must write contents to disk before reassigning.
        self.validData = True #data in buffer is valid
        # self.processing = False #Kernel is reading/writing context to disk

    def isLocked(self):
        return self.locked
    
    def isDelayedWrite(self):
        return self.delayWrite

    def isDataValid(self):
        return self.validData

    def updateBlockNumber(self, blockNumber):
        self.blockNumber = blockNumber

    def lock(self):
        if not self.isLocked():
            self.locked = True

    def unlock(self):
        if self.isLocked():
            self.locked = False

    def modifyData(self, data):
        self.data = data
        self.delayWrite = True
    
    def __repr__(self):
        return f'[Block:{self.blockNumber}|Data:"{self.data}"|Lock:{self.isLocked()}|DelayWrite:{self.isDelayedWrite()}]'