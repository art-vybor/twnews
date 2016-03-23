import logging
from time import time
from twnews.logs import log_string


def timeit(method):
    def timed(*args, **kw):
        logging.info(log_string('Function {FUNC} started with time measure'.format(FUNC=method.__name__)))

        start = time()
        result = method(*args, **kw)
        end = time()

        total_seconds = end-start
        minutes = int(total_seconds / 60)
        seconds = total_seconds - minutes * 60

        logging.info(log_string('Function {FUNC} finished in {MINUTES}m{SECONDS}s'.format(
            FUNC=method.__name__,
            MINUTES=minutes,
            SECONDS=seconds)))
        return result
    return timed
