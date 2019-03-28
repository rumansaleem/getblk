from buffer_structures import BufferCache
from threading import Event, Thread
from wait_control import WaitControl


class Worker(Thread):
    def __init__(self, processes = []):
        super(Worker, self).__init__()
        self.queued = processes
        self.started = []
        self.waitControl = WaitControl()

    def add(self, process):
        self.queued.append(process)
        # self.waitControl.wake("process:new")
    
    def run(self):
        while len(self.queued) > 0:
            process = self.queued.pop()
            process.start()
            self.started.append(process)
        
        [t.join() for t in self.started]

class DummyKernel:
    def __init__(self, bufferCache = BufferCache(20)):
        self.bufferCache = bufferCache
        self.waitControl = WaitControl()
        self.worker = Worker()

    def addProcess(self, process):
        self.worker.add(process)

    def addProcesses(self, processList):
        [self.worker.add(process) for process in processList]

    def boot(self):
        self.worker.start()
        self.worker.join()
        print("\n\n", "End of Op", "\n", self.bufferCache, "\n\n")
        
    def getblk(self, blockNumber, pid = "unknown"):
        """
        getblk algo from textbook
        """
        while(True):
            if self.bufferCache.hashQueue.has(blockNumber):
                buffer = self.bufferCache.hashQueue.get(blockNumber)
                if buffer.isLocked(): 
                    print(f'PID[{pid}] - getblk: accessing |Block:{blockNumber}|, resulted in "Scenario 5"')
                    # print("Scenario 5: Block was found on the hash queue, but its buffer is currently busy.")
                    # sleep until this buffer becomes free
                    self.waitControl.sleep(WaitControl.EVENT_WAIT_SPECIFIC_BUFFER(blockNumber))
                    self.waitControl.clear(WaitControl.EVENT_WAIT_SPECIFIC_BUFFER(blockNumber))
                    continue # return 3 , buffer #block on hashQ but busy
                
                # Scenario 1
                buffer.lock()
                self.bufferCache.freeList.remove(buffer)
                print(f'PID[{pid}] - getblk: accessing |Block:{blockNumber}|, resulted in "Scenario 1"')
                # print("Scenario 1: Block is found on its hash queue and its buffer is free.")
                return buffer  #block found on hashQ

            else:
                if self.bufferCache.freeList.isEmpty():
                    print(f'PID[{pid}] - getblk: accessing |Block:{blockNumber}|, resulted in "Scenario 4"')
                    # print('Scenario 4: Block could not be found on the hash queue and the free list of buffers is empty.')
                    # Sleep until any buffer becomes free
                    self.waitControl.sleep(WaitControl.EVENT_WAIT_ANY_BUFFER)  
                    self.waitControl.clear(WaitControl.EVENT_WAIT_ANY_BUFFER)
                    continue # return 0 , None
                else:
                    buffer = self.bufferCache.freeList.pop()
                    # Scenario 3
                    if buffer.isDelayedWrite():  
                        print(f'PID[{pid}] - getblk: accessing |Block:{blockNumber}|, resulted in "Scenario 3"')
                        # print('Scenario 3: Buffer not found on hash queue, buffer obtained from free list is marked "delay write"')
                        # Todo: write buffer asynchronously to the disk
                        continue
                    
                    print(f'PID[{pid}] - getblk: accessing |Block:{blockNumber}|, resulted in "Scenario 2"')
                    # print("Scenario 2: Buffer not found on hash queue but a buffer from free list is assigned")
                    if buffer.blockNumber:
                        self.bufferCache.hashQueue.remove(buffer)
                    buffer.lock()
                    buffer.updateBlockNumber(blockNumber)
                    self.bufferCache.hashQueue.add(buffer)
                    return buffer # block not in hashQ, taken from freelist

    def brelse(self, buffer, pid="unknown"):
        # Todo: wakeup all processes (event: waiting for any buffer to become free;
        self.waitControl.wake(WaitControl.EVENT_WAIT_ANY_BUFFER)
        # Todo: wakeup all processes (event: waiting for this buffer to become free;
        self.waitControl.wake(WaitControl.EVENT_WAIT_SPECIFIC_BUFFER(buffer.blockNumber))

        # raise processor execution level to block interrupts;
        if not buffer.isDelayedWrite():
            # enqueue buffer at end of free list;
            buffer.delayWrite = False
            self.bufferCache.freeList.push(buffer)
        else:
            # enqueue buffer at beginning of free list;
            self.bufferCache.freeList.unshift(buffer)
        # lower processor execution level to allow interrupts;
        buffer.unlock()
        return buffer

    def bread(self, blockNumber, pid="unknown"):
        print(f"PID[{pid}]: reading [block number {blockNumber}] into buffer from disk")

        buffer  = self.getblk(blockNumber, pid)
        if buffer.isDataValid():
            return buffer
        # self.buffer.data = self.disk.read(self.budd)
        # initiate disk read
        # sleep (event: disk read complete);
        return buffer

    def bwrite(self, buffer, pid="unknown"):
        # initiate disk write;
        # self.disk.write(buffer.blockNumber, buffer.data)
        print(f"PID[{pid}]: writing buffer {buffer} to disk")

        if (True): # I/O synchronous
            # sleep (event: I/O complete);
            self.brelse(buffer, pid)
        elif buffer.isDelayedWrite():
            buffer.delayWrite = False
            self.bufferCache.freeList.unshift(buffer)
            # mark buffer to put at head of free list;