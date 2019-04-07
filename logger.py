import logging

# fomatter for logging
formatter = logging.Formatter('[%(relativeCreated)d] [%(threadName)s]: %(message)s')

# logging.basicConfig(level=logging.INFO, format=)
# Get logger for program activity logging
logger = logging.getLogger("Activity Logger")
logger.setLevel(logging.DEBUG)

# File handler for logger
fileHandler = logging.FileHandler('kernel.log', mode='w')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)

# Console handler for logger
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)

# Add handlers to console
logger.addHandler(consoleHandler)
logger.addHandler(fileHandler)