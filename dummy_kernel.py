from buffer_structures.buffer_cache import BufferCache
from threading import Event, Thread
from event_bus import EventBus
from disk import Disk
import time

class Worker(Thread):
    def __init__(self, processes = []):
        super(Worker, self).__init__(daemon=True)
        self.queued = processes
        self.started = []
        self.completed = []
        self.eventBus = EventBus()

    def add(self, process):
        self.queued.append(process)
        # self.eventBus.wake("process:new")
    
    def run(self):
        while len(self.queued) > 0:
            process = self.queued.pop()
            process.start()
            self.started.append(process)
        
        for process in self.started:
            process.join()
            self.onCompleted(process)

    def onCompleted(self, process):
        self.started.remove(process)
        self.completed.append(process)
        print(f'PID[{process.pid}]: Exiting with success')

class DummyKernel:
    def __init__(self, bufferSize = 20, diskSize = 100):
        self.bufferCache = BufferCache(bufferSize)
        self.eventBus = EventBus()
        self.worker = Worker()
        self.disk = Disk(diskSize, self.eventBus)
        self.isRunning = False

    def addProcess(self, process):
        self.worker.add(process)

    def addProcesses(self, processList):
        [self.worker.add(process) for process in processList]

    def snapshot(self):
        while self.isRunning:
            time.sleep(1)
            print(
                "\n\n==========================\n", 
                "BufferCache Status:", 
                "\n", self.bufferCache, 
                "\n\n", "Disk:", 
                "\n", self.disk,
                "\n\n", "Event Bus:", "\n",
                "\n".join([f"[{event}]: {self.eventBus.isSet(event)}" for event in self.eventBus.events]),
                "\n\n", "Queued Processes:", "\n",
                "\n".join([str(p) for p in self.worker.queued]),
                "\n\n", "Active Processes:", "\n",
                "\n".join([str(p) for p in self.worker.started]),
                "\n\n", "Completed Processes:", "\n",
                "\n".join([str(p) for p in self.worker.completed]),
                "\n==========================\n\n"
            )

    def boot(self):
        self.isRunning = True
        snapshotter = Thread(None, self.snapshot, None)
        snapshotter.start()
        self.worker.start()
        self.worker.join()

        print("Shutting down Kernel...\nSaving 'delay-write' buffers to disk...\n")
        
        for buffer in self.bufferCache.__buffers__:
            print(f'Kernel: Examining the buffer {buffer} for "delayed-write"')
            if buffer.isDelayedWrite():
                self.disk.writeBuffer(buffer)

        self.isRunning = False
        snapshotter.join()
        print("\n\n", "==============Kernel Shutdown===============", "\n\n")
        
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
                    self.eventBus.sleep(EventBus.EVENT_WAIT_SPECIFIC_BUFFER(blockNumber))
                    self.eventBus.clear(EventBus.EVENT_WAIT_SPECIFIC_BUFFER(blockNumber))
                    continue
                
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
                    self.eventBus.sleep(EventBus.EVENT_WAIT_ANY_BUFFER)  
                    self.eventBus.clear(EventBus.EVENT_WAIT_ANY_BUFFER)
                    continue
                else:
                    buffer = self.bufferCache.freeList.pop()
                    # Scenario 3
                    if buffer.isDelayedWrite():  
                        print(f'PID[{pid}] - getblk: accessing |Block:{blockNumber}|, resulted in "Scenario 3"')
                        # write buffer asynchronously to the disk
                        asyncWriteThread = Thread(None, self.bwrite, "bwrite", (buffer, pid))
                        asyncWriteThread.start()
                        continue
                    
                    print(f'PID[{pid}] - getblk: accessing |Block:{blockNumber}|, resulted in "Scenario 2"')
                    # print("Scenario 2: Buffer not found on hash queue but a buffer from free list is assigned")
                    if buffer.blockNumber:
                        self.bufferCache.hashQueue.remove(buffer)
                    buffer.lock()
                    buffer.updateBlockNumber(blockNumber)
                    self.bufferCache.hashQueue.add(buffer)
                    return buffer # block not in hashQ, taken from freelist
            time.sleep(.5)

    def brelse(self, buffer, pid="unknown"):
        # Todo: wakeup all processes (event: waiting for any buffer to become free;
        self.eventBus.wake(EventBus.EVENT_WAIT_ANY_BUFFER)
        # Todo: wakeup all processes (event: waiting for this buffer to become free;
        self.eventBus.wake(EventBus.EVENT_WAIT_SPECIFIC_BUFFER(buffer.blockNumber))

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
        # initiate disk read
        buffer.data = self.disk.read(buffer.blockNumber)

        return buffer

    def bwrite(self, buffer, pid="unknown"):
        print(f"PID[{pid}]: asynchronously writing buffer {buffer} to disk")
        # initiate disk write;
        self.disk.writeBuffer(buffer)

        if not self.eventBus.isSet(Disk.EVENT_IO_COMPLETE): # I/O synchronous
            # sleep (event: I/O complete);
            self.eventBus.sleep(Disk.EVENT_IO_COMPLETE)
            self.brelse(buffer, pid)
        elif buffer.isDelayedWrite():
            buffer.delayWrite = False
            self.bufferCache.freeList.unshift(buffer)
            # mark buffer to put at head of free list;