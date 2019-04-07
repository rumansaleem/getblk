from buffer_structures.buffer_cache import BufferCache
from threading import Event, Thread
from event_bus import EventBus
from disk import Disk
from logger import logger
import time

class Worker(Thread):
    """
    Worker class for starting all processes in the job queue
    """
    def __init__(self, processes = []):
        super(Worker, self).__init__(daemon=True)
        self.queued = processes
        self.started = []
        self.eventBus = EventBus()

    def add(self, process):
        self.queued.append(process)
        # self.eventBus.wake("process:new")
    
    def run(self):
        while len(self.queued) > 0:
        	#pop from head, not the tail
            process = self.queued.pop(0)
            process.start()
            self.started.append(process)
        
        for process in self.started:
            process.join()

class Kernel:
    """
    Kernel class for emulating kernel
    """
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
        """
        Function that implements the logger, gives us a view of the 
        variables and data structures in our program at every step
        """
        while self.isRunning:
            time.sleep(1.0)
            eventBus = "\n".join([f"[{event}]: {self.eventBus.isSet(event)}" for event in self.eventBus.events])
            aliveProcesses = "\n".join([str(p) for p in self.worker.started if p.isAlive()])
            exitedProcesses = "\n".join([str(p) for p in self.worker.started if not p.isAlive()])
            logger.info("==========================")
            logger.info("BufferCache Status:")
            logger.info(f"{self.bufferCache}")
            logger.info("")
            logger.info("Disk:")
            logger.info(f"{self.disk}")
            logger.info("")
            logger.info("Event Bus:")
            logger.info(f"{eventBus}")
            logger.info("")
            logger.info("Alive Processes:")
            logger.info(f"{aliveProcesses}")
            logger.info("")
            logger.info("Exited Processes:")
            logger.info(f"{exitedProcesses}")
            logger.info("==========================")

    def boot(self):
        self.isRunning = True
        
        #Starts snapshotter thread
        snapshotter = Thread(None, self.snapshot, "Snapshotter")
        snapshotter.start()

        #starts processs thread
        self.worker.start()
        self.worker.join()

        logger.info("Shutting down Kernel...\nSaving 'delay-write' buffers to disk...\n")
        
        #After running all processes, writes all changes to the disk
        for buffer in self.bufferCache.__buffers__:
            logger.info(f'Kernel: Examining the buffer {buffer} for "delayed-write"')
            if buffer.isDelayedWrite():
                self.disk.writeBuffer(buffer)

        time.sleep(1)
        self.isRunning = False
        snapshotter.join()
        time.sleep(1)
        logger.info("\n\n==============Kernel Shutdown===============\n")
        
    def getblk(self, blockNumber):
        """
        getblk algo from textbook
        """
        while(True):
            if self.bufferCache.hashQueue.has(blockNumber):
                buffer = self.bufferCache.hashQueue.get(blockNumber)
                if buffer.isLocked(): 
                    logger.info(f'getblk(): accessing |Block:{blockNumber}|, resulted in "Scenario 5"')
                    # logger.info("Scenario 5: Block was found on the hash queue, but its buffer is currently busy.")
                    # sleep until this buffer becomes free
                    self.eventBus.sleep(EventBus.EVENT_WAIT_SPECIFIC_BUFFER(buffer))
                    self.eventBus.clear(EventBus.EVENT_WAIT_SPECIFIC_BUFFER(buffer))
                    continue
                
                # Scenario 1
                buffer.lock()
                self.bufferCache.freeList.remove(buffer)
                logger.info(f'getblk(): accessing |Block:{blockNumber}|, resulted in "Scenario 1"')
                # logger.info("Scenario 1: Block is found on its hash queue and its buffer is free.")
                return buffer  #block found on hashQ

            else:
                if self.bufferCache.freeList.isEmpty():
                    logger.info(f'getblk(): accessing |Block:{blockNumber}|, resulted in "Scenario 4"')
                    # logger.info('Scenario 4: Block could not be found on the hash queue and the free list of buffers is empty.')
                    # Sleep until any buffer becomes free
                    self.eventBus.sleep(EventBus.EVENT_WAIT_ANY_BUFFER)  
                    self.eventBus.clear(EventBus.EVENT_WAIT_ANY_BUFFER)
                    continue
                else:
                    buffer = self.bufferCache.freeList.pop()
                    # Scenario 3
                    if buffer.isDelayedWrite():  
                        logger.info(f'getblk(): accessing |Block:{blockNumber}|, resulted in "Scenario 3"')
                        # write buffer asynchronously to the disk
                        self.bwrite(buffer, synchronous=False)
                        continue
                    
                    buffer.lock()
                    logger.info(f'getblk(): accessing |Block:{blockNumber}|, resulted in "Scenario 2"')
                    # logger.info("Scenario 2: Buffer not found on hash queue but a buffer from free list is assigned")
                    if buffer.blockNumber:
                        self.bufferCache.hashQueue.remove(buffer)
                    logger.debug(f'REMOVE BUFFER{buffer} - UPDATED HASH QUEUE:{self.bufferCache.hashQueue}')
                    buffer.updateBlockNumber(blockNumber)
                    self.bufferCache.hashQueue.add(buffer)
                    return buffer # block not in hashQ, taken from freelist
            time.sleep(.5)

    def brelse(self, buffer):
        # Todo: wakeup all processes (event: waiting for any buffer to become free;
        self.eventBus.wake(EventBus.EVENT_WAIT_ANY_BUFFER)
        # Todo: wakeup all processes (event: waiting for this buffer to become free;
        self.eventBus.wake(EventBus.EVENT_WAIT_SPECIFIC_BUFFER(buffer))

        # raise processor execution level to block interrupts;
        if buffer.isDataValid() and not buffer.isOld():
            # enqueue buffer at end of free list;
            self.bufferCache.freeList.push(buffer)
        else:
            # enqueue buffer at beginning of free list;
            self.bufferCache.freeList.unshift(buffer)
        # lower processor execution level to allow interrupts;
        
        buffer.unlock()
        return buffer

    def bread(self, blockNumber):
        logger.info(f"bread() - Reading [block number {blockNumber}] into buffer from disk")

        buffer = self.getblk(blockNumber)
        if buffer.isDataValid():
            return buffer
        # initiate disk read
        buffer.setValidData(self.disk.read(buffer.blockNumber))

        return buffer

    def bwrite(self, buffer, synchronous = False):
        # initiate disk write;
        writer = Thread(None, self.disk.writeBuffer, "DISK_IO_WRITE", [buffer])
        writer.start()
        logger.info(f"bwrite() - Asynchronously writing buffer {buffer} to disk")

        if not synchronous: # I/O synchronous
            # sleep (event: I/O complete);
            writer.join()
            self.brelse(buffer)
        elif buffer.isDelayedWrite():
            buffer.setOld(True)
            # mark buffer to put at head of free list;
            # self.bufferCache.freeList.unshift(buffer)