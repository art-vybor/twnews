from url_unshortener import unshorten_url_memo, unshorten_url
import threading
from url_analysis import get_urls

import shelve
import random
import Queue
from time import time

data_file = './resolve_url_map.shelve'
threads_num = 100
#batch_size = 1
data = shelve.open(data_file)
q = Queue.Queue()

# def task(urls):
#     return map(unshorten_url, urls)
    


# def split(l, batch_size):
#     result = []
#     for i in range(0,len(l),batch_size):
#         start = i
#         end = i + batch_size
#         #print start, end
#         result.append(l[start:end])
#     return result



if __name__ == '__main__':
    urls, line_count = get_urls()

    urls = urls#[:1000]
    num_of_urls = len(urls)
    #batches = split(urls, batch_size)
    
    start = time()
    
    while urls:
        threads = []
        for thread in range(0, threads_num):
            if urls:
                threads.append(threading.Thread(target=lambda q, url : q.put((url, unshorten_url(url))), args=(q, urls.pop(0),)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print '%s urls left' % len(urls)
        while not q.empty():
            url, full_url = q.get()
            data[url] = full_url

        data.sync()
    

    end = time()

    total = end - start
    rps = num_of_urls/total
    print 'threads: %d; time: %.2fs; rps: %.2f' % (threads_num, total, rps)

    print 'starting analyze errors'
    errors = 0
    fixed = 0
    for url, full_url in data.iteritems():
        if not data[url]:
            errors += 1
            data[url] = unshorten_url(url)
            if data[url]:
                fixed += 1

    print 'fixed %d/%d errors' % (fixed, errors)

    data.close()




