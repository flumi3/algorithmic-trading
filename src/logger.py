import sys
import logging

from logging import Logger, Formatter, StreamHandler


FORMATTER: Formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt="%d.%m.%Y %H:%M:%S")

# Create Logger
logger: Logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

# Info log console handler
console_handler: StreamHandler = StreamHandler(sys.stdout)  # Create handler
console_handler.setLevel(logging.INFO)  # Set level to INFO so every INFO log gets displayed in the stdout
console_handler.setFormatter(FORMATTER)  # Set formatting of the log output
logger.addHandler(console_handler)  # Add handler to the logger


def get_main_logger() -> logging.Logger:
    return logger
