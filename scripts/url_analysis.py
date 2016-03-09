import copy
import re
import operator
import urllib2
import pickle
from urlparse import urlparse
from collections import OrderedDict
import os

from urllib2 import HTTPError, URLError

memo_file = './memo'

if not os.path.isfile(memo_file):
    memo = {}
else:
    with open(memo_file) as f:
        memo = pickle.load(f)

print memo

urls = []

with open('../consumer/logs/ru') as f:
    for line in f:    
        try:
            line = line.decode('string_escape')
        except Exception:
            break
        #print line
        s = re.search("(?P<url>https?://[^\s]+)", line)
        if s:
            urls.append(s.group("url"))
        
print len(urls), len(set(urls))

def find_domain2(url):
    print url

    if url not in memo:
        resp = urllib2.urlopen(url)
        domain = urlparse(resp.url)[1]

        memo[url] = domain
        with open(memo_file, 'w') as f:
            pickle.dump(memo, f)
    return memo[url]

def print_result(res):
    res = copy.deepcopy(res)
    if 'ERROR' in res:
        del res['ERROR']
    sorted_res = sorted(res.items(), key=lambda x: len(x[1]), reverse=True)
    for domain, count in sorted_res[:10]:
        print domain, len(count), count
    print '--------'

res = {}

for url in urls:
    #print url
    try:
        
        #print resp.url
        domain = find_domain2(url)

        if domain in res:

            res[domain].append(url)
        else:
            res[domain] = []

        #print sorted(res.items(), key=operator.itemgetter(1), reverse=True)
        print_result(res)
    except (HTTPError, URLError) as e:
        memo[url] = 'ERROR'
        print 'ERROR: ', e, e.__class__

    
sorted_urls = sorted(res.items(), key=operator.itemgetter(1))
print sorted_urls


