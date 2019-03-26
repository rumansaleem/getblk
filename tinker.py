from bufferStructures import BufferCache
from process import Process

def getblk(bufferCache, blockNumber):
    """
    getblk algo from textbook
    """
    if bufferCache.hashQueue.has(blockNumber):
        buffer = bufferCache.hashQueue.get(blockNumber)
        if buffer.isLocked(): 
            print("Scenario 5: Block was found on the hash queue, but its buffer is currently busy.")
            # Todo: sleep until buffer becomes free
            return 3 , buffer #block on hashQ but busy
        
        # Scenario 1
        buffer.lock()
        # remove from freelist
        bufferCache.freeList.remove(buffer)
        print("Scenario 1: Block is found on its hash queue and its buffer is free.")
        return 1 , buffer  #block found on hashQ

    else:
        if bufferCache.freeList.isEmpty():
            print('Scenario 4: Block could not be found on the hash queue and the free list of buffers is empty.')
            # Todo: Sleep until any buffer becomes free
            return 0 , None
        else:
            buffer = bufferCache.freeList.pop()
            # Scenario 3
            if buffer.isDelayedWrite():  
                print('Scenario 3: Buffer not found on hash queue, buffer obtained from free list is marked "delay write"')
                # write buffer asynchronously to the disk
                return 2 , buffer                 #delayed write
            
            print("Scenario 2: Buffer not found on hash queue but a buffer from free list is assigned")
            if buffer.blockNumber:
                bufferCache.hashQueue.remove(buffer)
            buffer.lock()
            buffer.updateBlockNumber(blockNumber)
            bufferCache.hashQueue.add(buffer)
            return 1 , buffer # block not in hashQ, taken from freelist

def brlse(BufferCache, buffer):
    # Todo: wakeup all processes (event: waiting for any buffer to become free;
    # Todo: wakeup all processes (event: waiting for this buffer to become free;
    # raise processor execution level to block interrupts;
    if not buffer.isDelayedWrite():
        # enqueue buffer at end of free list;
        bufferCache.freeList.push(buffer)
    else:
        # enqueue buffer at beginning of free list;
        bufferCache.freeList.unshift(buffer)
    # lower processor execution level to allow interrupts;
    buffer.unlock()
    return buffer

bufferCache = BufferCache()

print("[Get block 120]", getblk(bufferCache, 120), "\n")
print("[Get block 131]", getblk(bufferCache, 131), "\n")
print("[Get block 142]", getblk(bufferCache, 142), "\n")
print("[Get block 152]", getblk(bufferCache, 152), "\n")

status, buffer = getblk(bufferCache, 120)
print("[Get block 120]", (status, buffer), "\n")
print("[Release Block 120]", brlse(bufferCache, buffer), "\n")
print("[Get block 120]", getblk(bufferCache, 120), "\n\n")
