import logging


def log_and_print(log_level, msg):
    print msg
    logging.log(log_level, msg)