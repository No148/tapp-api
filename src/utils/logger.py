import logging
import sys

from utils.env import ENVIRONMENT_NAME

formatter = logging.Formatter(
    fmt='%(asctime)s %(name)s: [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# handlers
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('app.log')

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger = logging.getLogger()

logger.handlers = [
    stream_handler
]

if ENVIRONMENT_NAME == 'local':
    logger.handlers.append(file_handler)

logger.level = logging.INFO
