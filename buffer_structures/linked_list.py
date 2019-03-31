class LinkedList:
    def __init__(self):
        self.__items__ = []

    def __iter__(self):
        return iter(self.__items__)

    def push(self, item):
        if item not in self.__items__:
            self.__items__.append(item)

    def unshift(self,item):
        """
        Inserts element to the beginning of list
        """
        if item not in self.__items__:
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
        if item in self.__items__:
            return self.__items__.remove(item)

    def isEmpty(self):
        return  False if len(self.__items__) > 0 else True

    def __repr__(self):
        return "\n ".join([ str(item) for item in self.__items__])
