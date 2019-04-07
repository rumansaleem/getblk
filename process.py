from threading import Thread
from logger import logger
import time

class IORequest:
    """
    Represents a I/O Request.
    Read/Write request for a specific block number.
    """
    READ_IO = "read"
    WRITE_IO = "write"
    def __init__(self, blockNumber, io_type):
        self.blockNumber = blockNumber
        self.type = io_type

    def isRead(self):
        return self.type == IORequest.READ_IO
    
    def isWrite(self):
        return self.type == IORequest.WRITE_IO

    def __repr__(self):
        return f'{self.type.upper()} BLK-{self.blockNumber}'

class Process (Thread):
    """
    Process class
    """
    def __init__(self, kernel, pid, requests = [], ttl = None):
        super(Process, self).__init__(daemon=True, name=f"PID-{pid}")
        self.kernel = kernel
        self.buffer = None
        self.pid = pid
        self.requests = requests
        self.ttl = None

    def run(self):
        """
        Function for running process
        """
        logger.info(f'Process Started')

        # satisfy each request
        for request in self.requests:
            # Read block
            if request.isRead():
                logger.info(f'Read Request <- {request.blockNumber}')
                self.buffer = self.kernel.bread(request.blockNumber)  

            # Write Block
            elif request.isWrite():                     
                logger.info(f'Write Request -> {request.blockNumber}')
                self.buffer = self.kernel.getblk(request.blockNumber)
                self.buffer.modifyData(f'PID[{self.pid}]')
                
            self.kernel.brelse(self.buffer)                     
        
            if self.ttl:
                self.ttl -= 0.5
            
            time.sleep(0.5)

        # if still time left, work and sleep
        while self.ttl != None and self.ttl > 0:
            time.sleep(0.5)
            logger.info("Working...!")
            self.ttl -= 0.5


        # release buffer afterwards    
        logger.info('Exiting with success!')

    def __repr__(self):
        requests = f'[{"".join([str(r) for r in self.requests])}]'
        return f'[PID:{self.pid}, Requests:{requests}, Buffer:{self.buffer}, TTL:{self.ttl}]'