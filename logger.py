import logging

formatter = logging.Formatter('[%(relativeCreated)d] [%(threadName)s]: %(message)s')
# logging.basicConfig(level=logging.INFO, format=)
logger = logging.getLogger("Activity Logger")
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler('kernel.log', mode='w')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)

logger.addHandler(consoleHandler)
logger.addHandler(fileHandler)