import sys
import logging

from logging import Formatter, Logger, StreamHandler


FORMATTER: Formatter = Formatter('%(asctime)s - %(levelname)s - [%(module)s.py]: %(message)s',
                                 datefmt="%d.%m.%Y %H:%M:%S")

# Create Logger
logger: Logger = logging.getLogger("__main__")
logger.setLevel(logging.INFO)

# Debug log console handler
console_handler: StreamHandler = StreamHandler(sys.stdout)  # Create handler
console_handler.setLevel(logging.DEBUG)  # Set level to DEBUG so every DEBUG log gets passed to the logger
console_handler.setFormatter(FORMATTER)  # Set formatting of the log output
logger.addHandler(console_handler)  # Add handler to the logger
