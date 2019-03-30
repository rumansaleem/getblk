from .buffer import Buffer
from .linked_list import LinkedList
from .hash_queue import HashQueue

class BufferCache:
    def __init__(self, buffer_count = 10):
        self.__buffers__ = [ Buffer(id) for id in range(1,buffer_count+1) ]
        self.freeList = LinkedList()
        self.hashQueue = HashQueue()
        for buffer in self.__buffers__:
            self.freeList.push(buffer)
    
    def __repr__(self):
        all_buffers = "\n".join([str(buffer) for buffer in self.__buffers__])
        return f'All Buffers:\n{all_buffers}\n\nFree List:\n{self.freeList}\n\nHash Queue:\n{self.hashQueue}\n'