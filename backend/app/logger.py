import logging
import sys

# Create logger
logger = logging.getLogger("boba-seeker")
logger.setLevel(logging.INFO)

# Create console handler and set level to info
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Add formatter to handler
handler.setFormatter(formatter)

# Add handler to logger
if not logger.handlers:
    logger.addHandler(handler)

# Export for easy use
__all__ = ["logger"]
