from buffer_structures import BufferCache
from process import Process

from dummy_kernel import DummyKernel

kernel = DummyKernel(10, 25)

kernel.addProcesses([
    Process(kernel, 4, 20, Process.IO_READ),
    Process(kernel, 1, 10, Process.IO_READ), 
    Process(kernel, 5, 10, Process.IO_READ),
    Process(kernel, 2, 20, Process.IO_WRITE),
    Process(kernel, 3, 10, Process.IO_WRITE),
])

kernel.boot()