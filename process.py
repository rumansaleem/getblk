from threading import Thread
import time
class Process (Thread):
    IO_READ = "read"
    IO_WRITE = "write"
    def __init__(self, kernel, pid, blockNumber, io = None, ttl = 1):
        super(Process, self).__init__(daemon=True)
        self.kernel = kernel
        self.buffer = None
        self.pid = pid
        self.blockNumber = blockNumber
        self.io = Process.IO_READ if io == None else io
        self.ttl = ttl

    def run(self):
        print(f'PID[{self.pid}]: Started')
        self.buffer = self.kernel.bread(self.blockNumber, self.pid)
        while self.ttl > 0:
            print(f'PID [{self.pid}]: Read {self.buffer}')
            time.sleep(1)
            self.ttl -= 1
        if self.io == Process.IO_WRITE:
            print(f'PID [{self.pid}]: Write to Buffer -> {self.buffer}')
            self.buffer.modifyData(f'PID[{self.pid}] TEXT')
        self.kernel.brelse(self.buffer, self.pid)

    def __repr__(self):
        return f'[PID:{self.pid}, Block:{self.blockNumber}, Buffer:{self.buffer}, IO:{self.io}, TTL:{self.ttl}]'