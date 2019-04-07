from threading import Thread
import time

"""
Disk and DiskBlock classes to emulate disk processes
"""
class DiskBlock:
    def __init__(self, number, data = None):
        self.number = number
        self.data = data

    def read(self):
        return self.data
    
    def write(self, data):
        self.data = data
 
    def __repr__(self):
        return f'[{self.number}:"{self.data}"]'


class Disk:
    # EVENT_IO_COMPLETE = "disk:io.done"

    def __init__(self, size, eventBus):
        self.size = size
        self.blockArray = [DiskBlock(i+1) for i in range(self.size)]
        self.eventBus = eventBus
        self.readBuffer = None

    def find(self, blockNumber):
        for block in self.blockArray:
            if block.number == blockNumber:
                return block
    
    def write(self, blockNumber, data, throttle = 0.10):
        # self.eventBus.sleep(Disk.EVENT_IO_COMPLETE, False)
        # self.eventBus.clear(Disk.EVENT_IO_COMPLETE)
        time.sleep(throttle)
        block = self.find(blockNumber)
        if block:
            block.write(data)
            # self.eventBus.wake(Disk.EVENT_IO_COMPLETE)
        else: 
            # self.eventBus.wake(Disk.EVENT_IO_COMPLETE)
            raise ValueError("Disk blockNumber out of bounds")

    def writeBuffer(self, buffer, throttle = 0.05):
        self.write(buffer.blockNumber, buffer.data, throttle)
        buffer.delayWrite = False
        
    def read(self, blockNumber, throttle = 1):
        # self.eventBus.sleep(Disk.EVENT_IO_COMPLETE)
        # self.eventBus.clear(Disk.EVENT_IO_COMPLETE)
        self.readBuffer = None
        time.sleep(throttle)
        block = self.find(blockNumber)
        self.readBuffer = block.read()
        return self.readBuffer
        # self.eventBus.set(Disk.EVENT_IO_COMPLETE)
        
    def __repr__(self):
        return "\n".join([str(blk) for blk in self.blockArray])
    