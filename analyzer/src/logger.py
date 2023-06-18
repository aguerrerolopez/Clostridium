import logging
import sys

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# Add STDOUT handler
formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
