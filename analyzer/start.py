import signal
import time
from src.analyzer import load_models, run_analyzer
from src.logger import logger
from src.models import download_models

# Time to wait between analyzer runs, in seconds
DELAY_BETWEEN_RUNS = 30

# Register stop handler
is_running = True
def stop_handler(sig, frame):
    global is_running
    if is_running:
        is_running = False
        logger.info('Received signal to stop analyzer')
    else:
        logger.warn('Already stopping, ignored signal')
signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGTERM, stop_handler)
logger.debug('Registered stop handler')

# Load models
download_models()
load_models()
logger.info('Started analyzer')

# Main loop
while is_running:
    run_analyzer()

    # Wait until next iteration
    for _ in range(DELAY_BETWEEN_RUNS):
        time.sleep(1)
        if not is_running:
            break

# Exit gracefully
logger.info('Stopped analyzer')
