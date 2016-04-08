from twnews.url_unshortener import unshorten_url
from twnews import defaults
import threading

import re
from itertools import chain
from urlparse import urlparse
from tabulate import tabulate


import shelve

import Queue
from time import time



def resolve_urls(data, q, urls, threads_count):
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

def filter_urls(data, urls):
    res = []
    for url in urls:
        if not (url in data and data[url]): # and data[url])
            res.append(url)
    return res


def resolve(tweets_path=defaults.TWEETS_PATH, resolve_path=defaults.RESOLVE_URL_MAP_PATH):
    data = shelve.open(resolve_path)
    q = Queue.Queue()

    urls, line_count = get_urls(tweets_path)

    urls = filter_urls(data, urls)

    total_urls = len(urls)
    start = time()

    for threads in [100, 10, 1]:
        if urls:
            urls = resolve_urls(data, q, urls, threads)

    end = time()

    total = end - start
    rps = total_urls/total
    print '-------------\n total: time: %.2fs; rps: %.2f; errors: %.2f%%' % (total, rps, len(urls)*1.0/(total_urls+1e-8))


    data.close()



def get_urls(tweets_path):
    urls = []
    line_count = 0
    with open(tweets_path) as f:
        for line in f:
            line_count+=1
            try:
                line = line.decode('string_escape')
            except Exception:
                break
            # if 'https://t.co/EXhvEUqeo' in line:
            #     import sys
            #     print line
            #     sys.exit(0)
            # all urls in twitters like this
            s = re.search('https?://t.co/[\w\d]{10}', line)
            if s:
                urls.append(s.group(0))
    return urls, line_count


def get_domain(url):
    return urlparse(url)[1]


def print_result(res, top_size=20):
    total_rows = len(list(chain(*res.values())))
    print 'TOP%d by %d rows' % (top_size, total_rows)
    sorted_res = sorted(res.items(), key=lambda x: len(x[1]), reverse=True)

    sum_percent = 0
    table = []
    for domain, count in sorted_res[:top_size]:
        percent = len(count)*100.0/total_rows
        #print '%s\t%s\t%.2f%%' % (domain, len(count), percent)#, count
        if not domain:
            domain = 'ERROR'
        table.append((domain, len(count), '%.02f' % percent))
        sum_percent+=percent

    print tabulate(table)

    print 'total_percent in TOP%s: %.2f' % (top_size, sum_percent)
    print '--------------------------------------'


def url_analyse(resolve_path=defaults.RESOLVE_URL_MAP_PATH, tweets_path=defaults.TWEETS_PATH):
    data = shelve.open(resolve_path)
    urls, line_count = get_urls(tweets_path)
    print line_count, len(urls), len(set(urls))

    res = {}
    count = 0
    #for url in urls:
    for url in data:
        full_url = data[url]
        domain = get_domain(full_url) if full_url else None

        if domain in res:
            res[domain].append(url)
        else:
            res[domain] = [url]

        count += 1
        # if count % 100 == 0:
            #     print_result(res)

    print_result(res)







