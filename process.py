from threading import Thread
import time

class Process (Thread):

    def __init__(self, kernel, pid, blockNumber, ttl = 10):
        super(Process, self).__init__()
        self.pid = pid
        self.kernel = kernel
        self.buffer = None
        self.ttl = ttl
        self.blockNumber = blockNumber

    def run(self):
        self.buffer = self.kernel.getblk(self.blockNumber, self.pid)
        while(self.ttl > 0):
            print(f'PID [{self.pid}]: Working with {self.buffer}')
            time.sleep(1)
            self.ttl -= 1
        self.buffer.data = f'Data written by: PID[{self.pid}]'
        self.kernel.bwrite(self.buffer, self.pid)