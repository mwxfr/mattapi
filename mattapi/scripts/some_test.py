import logging

from mattapi.api import *

logger = logging.getLogger(__name__)


def my_test():
    logger.error('Move mouse to 100, 100')
    hover(Location(100,100))

    logger.error('Move mouse to 100, 400')
    hover(Location(100,400))

    logger.error('Move mouse to 400, 100')
    hover(Location(400,100))

    logger.error('Move mouse to 400, 400')
    hover(Location(400,400))
