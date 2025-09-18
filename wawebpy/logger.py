import logging
import sys
from typing import Literal

# Create a global logger instance
logger = logging.getLogger("wawebpy")
logger.setLevel(logging.ERROR)  # Default level, can be overridden

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)  # Default console level

# Formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
ch.setFormatter(formatter)

# Add handler to the logger
if not logger.hasHandlers():
    logger.addHandler(ch)

def set_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]):
    """
    Set the logging level globally.
    Accepts 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    logger.setLevel(numeric_level)
    ch.setLevel(numeric_level)
