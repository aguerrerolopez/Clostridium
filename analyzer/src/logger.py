import logging
import os
import sys

# Create logger instance
level = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger('app')
logger.setLevel(level)

# Add STDOUT handler
formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
