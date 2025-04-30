import logging
import os
from datetime import datetime

def get_logger(service: str, level=logging.INFO):
    """
    Creates and returns a logger instance for the given service.
    Logs to both file and console.
    
    Args:
        service (str): Name of the service for logging
        level (int): Logging level (default: logging.INFO)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    os.makedirs("logs", exist_ok=True)

    log_file = f"logs/{service}.log"

    logger = logging.getLogger(service)
    logger.setLevel(level)

    # avoiding duplicate handlers
    if logger.hasHandlers():
        return logger
    
    # specify log format
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
