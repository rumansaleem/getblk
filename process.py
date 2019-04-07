from threading import Thread
from logger import logger
import time

class Process (Thread):
    """
    Process class
    """
    IO_READ = "read"
    IO_WRITE = "write"
    def __init__(self, kernel, pid, blockNumber, io = None, ttl = 1):
        super(Process, self).__init__(daemon=True, name=f"PID-{pid}")
        self.kernel = kernel
        self.buffer = None
        self.pid = pid
        self.blockNumber = blockNumber
        self.io = Process.IO_READ if io == None else io
        self.ttl = ttl

    def run(self):
        """
        Function for running process
        """
        logger.info(f'Process Started')

        # Obtain buffer and perform R/W
        self.buffer = self.kernel.bread(self.blockNumber)   
        
        # for simulating process running time
        while self.ttl > 0:
            logger.info(f'Reading {self.buffer}')
            time.sleep(0.5)
            self.ttl -= 0.5

        # perform write operation if required
        if self.io == Process.IO_WRITE:                     
            logger.info(f'Write to Buffer -> {self.buffer}')
            self.buffer.modifyData(f'PID[{self.pid}]')

        # release buffer afterwards    
        self.kernel.brelse(self.buffer)                     
        logger.info('Exiting with success!')

    def __repr__(self):
        return f'[PID:{self.pid}, Block:{self.blockNumber}, Buffer:{self.buffer}, IO:{self.io}, TTL:{self.ttl}]'