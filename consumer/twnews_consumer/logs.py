import logging
from twnews_consumer import defaults
from datetime import datetime

logging.basicConfig(filename=defaults.LOG_FILE, level=defaults.LOG_LEVEL)


def log_string(message):
    print message
    return '{DATE}: {MESSAGE}'.format(DATE=datetime.utcnow(), MESSAGE=message)