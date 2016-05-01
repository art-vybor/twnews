import Queue
import shelve
import threading


from itertools import chain
from urlparse import urlparse
from tabulate import tabulate

from time import time

from twnews.url_unshortener import unshorten_url
from twnews import defaults


def resolve_urls(resolve_map, q, links, threads_count):
    num_of_urls = len(links)
    error_urls = {}
    print 'resolve %d urls with %d threads' % (num_of_urls, threads_count)

    start = time()

    while links:
        threads = []
        for thread in range(0, threads_count):
            if links:
                threads.append(threading.Thread(target=lambda q, (link, url): q.put((link, unshorten_url(url))), args=(q, links.popitem(),)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        while not q.empty():
            url, full_url = q.get()

            resolve_map[url] = full_url
            if not full_url:
                error_urls[url] = url

        print 'urls left: %s, errors_count: %d' % (len(links), len(error_urls))

        resolve_map.sync()

    end = time()

    total = end - start
    rps = num_of_urls/total
    print 'threads: %d; time: %.2fs; rps: %.2f; errors: %.2f%%' % (threads_count, total, rps, len(error_urls)*1.0/num_of_urls)
    return error_urls


def filter_urls(data, urls):
    links = {}

    for url in urls:
        if not (url in data):# and data[url]):
            links[url] = urls[url]
    return links


def resolve(resolve_path=defaults.RESOLVE_URL_MAP_PATH, tweets_path=defaults.TWEETS_PATH, sample_size=None):
    resolve_map = shelve.open(resolve_path)
    links, media_links = get_urls(tweets_path, sample_size)

    q = Queue.Queue()

    links = filter_urls(resolve_map, links)

    total_urls = len(links)
    start = time()

    for threads_num in [100, 10]:
        if links:
            links = resolve_urls(resolve_map, q, links, threads_num)

    end = time()

    total = end - start
    rps = total_urls/total
    print '-------------\n total: time: %.2fs; rps: %.2f; errors: %.2f%%' % (total, rps, len(links)*1.0/(total_urls+1e-8))

    resolve_map.close()



def get_urls(tweets_path, sample_size=None):
    print tweets_path
    tweets = shelve.open(tweets_path)

    links = {}
    media_links = {}
    i = 0
    for tweet_id, tweet in tweets.iteritems():
        for url, res in tweet['links'].iteritems():
            res = res.encode('ascii', 'ignore')
            links[str(url)] = str(res)
        for url, res in tweet['media_links'].iteritems():
            media_links[str(url)] = str(res)

        i += 1
        if sample_size:
            if i >= sample_size:
                return links, media_links

    return links, media_links


def get_domain(url):
    return urlparse(url)[1]


def print_result(res, top_size=25):
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


def url_analyse(resolve_path=defaults.RESOLVE_URL_MAP_PATH):
    resolve_map = shelve.open(resolve_path)

    res = {}
    count = 0
    # for url in urls:
    for url in resolve_map:
        full_url = resolve_map[url]
        domain = get_domain(full_url) if full_url else None

        if domain in res:
            res[domain].append(url)
        else:
            res[domain] = [url]

        count += 1

    print_result(res)


# def test():
#     resolve_map = shelve.open(defaults.RESOLVE_URL_MAP_PATH)
#     links, media_links = get_urls(tweets_path=defaults.TWEETS_PATH, sample_size=100)
#     for link in links:
#         print link
#         print '\t%s' % links[link]
#         print '\t%s' % resolve_map[link]
# test()
    #resolve(sample_size=100)


#url_analyse()