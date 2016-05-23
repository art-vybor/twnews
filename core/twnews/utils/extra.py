import logging
from time import time
from multiprocessing import Queue, Process


def timeit(method):
    def timed(*args, **kw):
        logging.info('{FUNC} started with time measure'.format(
            FUNC=method.__name__))

        start = time()
        result = method(*args, **kw)
        end = time()

        total_seconds = end-start
        minutes = int(total_seconds / 60)
        seconds = total_seconds - minutes * 60

        logging.info('Function {FUNC} finished in {MINUTES}m{SECONDS}s'.format(
            FUNC=method.__name__,
            MINUTES=minutes,
            SECONDS=seconds))
        return result
    return timed


def progressbar_iterate(collection, step_percent=0.1):
    logging.info('iterate over collections with progressbar started')

    step_size = int(step_percent * len(collection))
    for i, item in enumerate(collection):
        if i % step_size == 0:
            progress = i*100.0/len(collection)
            logging.info('%.2f%% of iteration finished' % progress)
        yield item

    logging.info('100% of iteration finished')


def split_to_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    size = len(l)/n+1
    for i in range(0, len(l), size):
        yield l[i:i+size]

def result_collecter(f):
    def func(x, idx, q):
        result = f(x)
        print idx, 'finished'
        q.put_nowait((idx, result))
        print idx, 'result putted to queue'
    return func


def multiprocess_map(f, collection, num_of_process=16):
    collection = collection[:100]
    logging.info('Multiprocess map started')
    batchs = split_to_chunks(collection, num_of_process)

    result_queue = Queue()
    processes = []
    for idx, batch in enumerate(batchs):
        p = Process(target=result_collecter(f), args=(batch, idx, result_queue))
        processes.append(p)

    for p in processes:
        p.start()
    logging.info('processes spawned')

    for p in processes:
        p.join()
    logging.info('processes finished')

    raw_result = []
    while not result_queue.empty():
        raw_result.append(result_queue.get())
    raw_result = sorted(raw_result)
    logging.info('result sorted')

    result = []
    for _, x in raw_result:
        result.extend(x)
    logging.info('result collected')
    return result
