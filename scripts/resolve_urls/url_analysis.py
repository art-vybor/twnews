import copy
import re
import operator
import urllib2
from itertools import chain
from urlparse import urlparse
import httplib
from collections import OrderedDict

from url_unshortener import unshorten_url_memo

from urllib2 import HTTPError, URLError
from tabulate import tabulate


def get_urls(filepath='/home/avybornov/twnews_data/tweets'):
    urls = []
    line_count = 0
    with open(filepath) as f:
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


if __name__ == '__main__':
    import resolve_urls
    urls, line_count = get_urls()
    print line_count, len(urls), len(set(urls))

    res = {}
    count = 0
    #for url in urls:
    for url in resolve_urls.data:
        full_url = resolve_urls.data[url]
        domain = get_domain(full_url) if full_url else None

        if domain in res:
            res[domain].append(url)
        else:
            res[domain] = [url]

        count += 1
        # if count % 100 == 0:
            #     print_result(res)

    print_result(res)


