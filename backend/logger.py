import logging
from pythonjsonlogger import jsonlogger

def setup_logger():
    logger = logging.getLogger("closira")
    logger.setLevel(logging.INFO)

    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
    logHandler.setFormatter(formatter)

    # Remove existing handlers to prevent duplicates if instantiated multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(logHandler)
    return logger

logger = setup_logger()
