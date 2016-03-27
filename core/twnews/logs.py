import logging
from twnews import defaults
from datetime import datetime


logging.basicConfig(filename=defaults.LOG_FILE, level=defaults.LOG_LEVEL)


def log_string(message):
    log_str = '{DATE}: {MESSAGE}'.format(DATE=datetime.utcnow(), MESSAGE=message)
    print log_str
    return log_str
