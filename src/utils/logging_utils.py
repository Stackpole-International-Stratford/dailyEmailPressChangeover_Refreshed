# src/utils/logging_utils.py

from loguru import logger

def setup_logger():
    logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")
    return logger
