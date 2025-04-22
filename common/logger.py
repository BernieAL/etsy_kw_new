import logging
import os
from datetime import datetime

def get_logger(service: str, level=logging.INFO):
    
    os.makedirs("logs",exist_ok=True)

    log_file = f"logs/{service}.log"

    logger = logging.getLogger(service)
    logger.setLevel(level)

    #avoiding duplicate handlers
    if logger.hasHandlers():
        return logger
    
    #specify log format
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    #open given file and use it as stream to output to
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
