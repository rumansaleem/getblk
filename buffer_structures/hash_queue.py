from .linked_list import LinkedList
from logger import logger

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
        return "\n ".join([ f"[blkno mod {self.size} = {key}]\n{self.__hashTable__[key]}"  for key in self.__hashTable__])
