"""Simple logging setup for web2md tool."""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
