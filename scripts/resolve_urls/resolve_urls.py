from url_unshortener import unshorten_url_memo, unshorten_url
import threading
from url_analysis import get_urls

import shelve
import random
import Queue
from time import time

data_file = './resolve_url_map.shelve'
#threads_num = 100
#batch_size = 1
data = shelve.open(data_file)
q = Queue.Queue()


def resolve_urls(urls, threads_count):
    num_of_urls = len(urls)
    error_urls = []
    print 'analyze %d urls with %d threads' % (num_of_urls, threads_count)
    
    #batches = split(urls, batch_size)
    
    start = time()
    
    while urls:
        threads = []
        for thread in range(0, threads_count):
            if urls:
                threads.append(threading.Thread(target=lambda q, url : q.put((url, unshorten_url(url))), args=(q, urls.pop(0),)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print 'urls left: %s, errors_count: %d' % (len(urls), len(error_urls))

        while not q.empty():
            url, full_url = q.get()

            data[url] = full_url
            if not full_url:
                error_urls.append(url)
        data.sync()
    

    end = time()

    total = end - start
    rps = num_of_urls/total
    print 'threads: %d; time: %.2fs; rps: %.2f; errors: %.2f%%' % (threads_count, total, rps, len(error_urls)*1.0/num_of_urls)
    return error_urls

def filter_urls(urls):
    res = []
    for url in urls:
        if not (url in data and data[url]): # and data[url])
            res.append(url)
    return res


if __name__ == '__main__':
    urls, line_count = get_urls()

    urls = urls

    urls = filter_urls(urls)

    total_urls = len(urls)
    start = time()

    for threads in [100, 10, 1]:
        if urls:
            urls = resolve_urls(urls, threads)

    end = time()

    total = end - start
    rps = total_urls/total
    print '-------------\n total: time: %.2fs; rps: %.2f; errors: %.2f%%' % (total, rps, len(urls)*1.0/(total_urls+1e-8))
    # print 'starting analyze errors'
    # errors = 0
    # fixed = 0
    # for url, full_url in data.iteritems():
    #     if not data[url]:
    #         errors += 1
    #         data[url] = unshorten_url(url)
    #         if data[url]:
    #             fixed += 1

    # print 'fixed %d/%d errors' % (fixed, errors)

    data.close()




