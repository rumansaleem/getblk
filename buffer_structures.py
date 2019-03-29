class BufferHeaderNode:
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

class LinkedList:
    def __init__(self):
        self.__items__ = []

    def __iter__(self):
        return iter(self.__items__)

    def push(self, item):
        self.__items__.append(item)

    def unshift(self,item):
        """
        Inserts element to the beginning of list
        """
        self.__items__.insert(0, item)

    def pop(self):
        """
        pops element from the beginning of list
        """
        return self.__items__.pop(0)

    def shift(self):
        """
        Removes Element from the end of list
        """
        end = len(self.__items__)
        if end:
            return self.__items__.pop(end - 1)

    def findIndexByBlockNumber(self, blockNumber):
        for i in range(len(self.__items__)):
            if self.__items__[i].blockNumber == blockNumber: 
                return i
    def findByBlockNumber(self, blockNumber):
        index = self.findIndexByBlockNumber(blockNumber)
        if isinstance(index, int):
            return self.__items__[index]

    def remove(self, item):
        """
        Removes first element that matches the given matcher
        """
        index = self.findIndexByBlockNumber(item.blockNumber)

        if index:
            return self.__items__.pop(index)

    def isEmpty(self):
        return  False if len(self.__items__) > 0 else True

    def __repr__(self):
        return "\n     ".join([ str(item) for item in self.__items__])
        
class HashQueue:
    def __init__(self):
        self.size = 4
        self.__hashTable__ = {}

    def hash(self, key):
        return key % self.size

    def get(self, key):
        queue = self.__hashTable__[self.hash(key)]
        return queue.findByBlockNumber(key)

    def add(self, buffer):
        hashKey = self.hash(buffer.blockNumber)

        if hashKey not in self.__hashTable__:
            self.__hashTable__[hashKey] = LinkedList()
            
        self.__hashTable__[hashKey].push(buffer)

    def has(self, key):
        hashKey = self.hash(key)

        if hashKey not in self.__hashTable__:
            return False
            
        for item in self.__hashTable__[hashKey]:
            if item.blockNumber == key:
                return True
        return False

    def remove(self, buffer):
        """
        Inserts element to the beginning of list
        """
        hashKey = self.hash(buffer.blockNumber)

        return self.__hashTable__[hashKey].remove(buffer)

    def __repr__(self):
        return "\n".join([ "[" + str(key) + "] : " + str(self.__hashTable__[key])  for key in self.__hashTable__])

class BufferCache:
    def __init__(self, buffer_count = 10):
        self.__buffers__ = dict([ (id, BufferHeaderNode(id)) for id in range(1,buffer_count+1) ])
        self.freeList = LinkedList()
        self.hashQueue = HashQueue()
        for key in self.__buffers__:
            self.freeList.push(self.__buffers__[key])
    
    def __repr__(self):
        return f'All Buffers:\n{self.__buffers__}\n\nFree List:\n{self.freeList}\n\nHash Queue:\n{self.hashQueue}\n'