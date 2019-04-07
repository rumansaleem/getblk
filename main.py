from process import Process
from kernel import Kernel

#initialize kernel
kernel = Kernel(bufferSize=5, diskSize=10)

#add processes to kernel
kernel.addProcesses([
    Process(kernel, pid = 108, blockNumber = 1, io=Process.IO_WRITE),
    Process(kernel, pid = 101, blockNumber = 1, io=Process.IO_WRITE), 
    Process(kernel, pid = 102, blockNumber = 2, io=Process.IO_WRITE),
    Process(kernel, pid = 103, blockNumber = 3, io=Process.IO_WRITE),
    Process(kernel, pid = 109, blockNumber = 8, io=Process.IO_WRITE),
    Process(kernel, pid = 110, blockNumber = 4, io=Process.IO_WRITE),
    Process(kernel, pid = 104, blockNumber = 4, io=Process.IO_WRITE),
    Process(kernel, pid = 105, blockNumber = 5, io=Process.IO_WRITE),
    Process(kernel, pid = 106, blockNumber = 3, io=Process.IO_WRITE),
    Process(kernel, pid = 107, blockNumber = 4, io=Process.IO_READ),
])

# kernel.addProcesses([
#     Process(kernel, pid = 101, blockNumber = 1, io=Process.IO_WRITE),
#     Process(kernel, pid = 102, blockNumber = 2, io=Process.IO_WRITE),
#     Process(kernel, pid = 103, blockNumber = 3, io=Process.IO_WRITE)
# ]) 

kernel.boot()
# from buffer_structures.hash_queue import HashQueue
# from buffer_structures.buffer import Buffer
# hashQ = HashQueue()
# buffer = Buffer(2)
# buffer.updateBlockNumber(2)
# hashQ.add(buffer)
# print(hashQ.remove(buffer))
# print(hashQ)