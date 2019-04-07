from process import Process, IORequest
from kernel import Kernel

#initialize kernel
kernel = Kernel(bufferSize=5, diskSize=10)

#add processes to kernel
kernel.addProcesses([
    Process(kernel, pid = 101, requests=[
        IORequest(blockNumber = 1, io_type=IORequest.WRITE_IO)
    ]),
    Process(kernel, pid = 102, requests=[
        IORequest(blockNumber = 2, io_type=IORequest.WRITE_IO)
    ]),
    Process(kernel, pid = 103, requests=[
        IORequest(blockNumber = 3, io_type=IORequest.READ_IO)
    ]),
    Process(kernel, pid = 106, requests=[
        IORequest(blockNumber = 3, io_type=IORequest.WRITE_IO)
    ]),
    Process(kernel, pid = 107, requests=[
        IORequest(blockNumber = 4, io_type=IORequest.READ_IO),
        IORequest(blockNumber = 4, io_type=IORequest.WRITE_IO),
        IORequest(blockNumber = 5, io_type=IORequest.WRITE_IO),
    ]),
])

kernel.boot()