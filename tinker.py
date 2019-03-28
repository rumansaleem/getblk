from buffer_structures import BufferCache
from process import Process

from dummy_kernel import DummyKernel

kernel = DummyKernel(BufferCache(10))

kernel.addProcesses([
    Process(kernel, 1, 10, 1), 
    Process(kernel, 2, 20, 1),
    Process(kernel, 3, 10, 1),
    Process(kernel, 4, 20, 1),
    Process(kernel, 5, 10, 1),
])

kernel.boot()