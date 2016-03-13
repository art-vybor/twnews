import copy
import re
import operator
import urllib2
import pickle
from urlparse import urlparse
import httplib
from collections import OrderedDict
import os

from urllib2 import HTTPError, URLError

memo_file = './memo'

if not os.path.isfile(memo_file):
    memo = {}
else:
    with open(memo_file) as f:
        memo = pickle.load(f)

#print memo

def add_to_memo(url, domain):
    memo[url] = domain
    with open(memo_file, 'w') as f:
        pickle.dump(memo, f)

urls = []
line_count = 0
with open('../consumer/logs/ru') as f:
    for line in f:    
        line_count+=1
        try:
            line = line.decode('string_escape')
        except Exception:
            break
        #print line
        s = re.search("(?P<url>https?://[^\s]+)", line)
        if s:
            urls.append(s.group("url"))
        
print line_count, len(urls), len(set(urls))

def unshorten_url(url):
    parsed = urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc, timeout=4)

    try:
        h.request('HEAD', parsed.path)
        response = h.getresponse()
    except Exception as e:
        print 'ERROR: ', e, e.__class__
        return None    
    
    #print response.getheaders()
    #print '-------'
    if response.getheader('Location') == url:
        return url
    elif response.getheader('Location'):
        return unshorten_url(response.getheader('Location'))

    return url

# for url in urls:
#     print '%s -> %s' % (url,unshorten_url(url))
#     try:
#         print urllib2.urlopen(url).url
#     except:
#         print 'ERROR'

#     print '-----'

def find_domain2(url):
    if url not in memo:
        #print url
        short_url = unshorten_url(url)
        if short_url:
            domain = urlparse(short_url)[1]
            #print domain

            add_to_memo(url, domain)
        else:
            add_to_memo(url, 'ERROR')

    return memo[url]

def print_result(res):
    res = copy.deepcopy(res)
    if 'ERROR' in res:
        del res['ERROR']
    sorted_res = sorted(res.items(), key=lambda x: len(x[1]), reverse=True)
    sum_percent = 0
    for domain, count in sorted_res[:20]:
        percent = len(count)*100.0/len(urls)
        print '%s\t%s\t%.2f%%' % (domain, len(count), percent)#, count
        sum_percent+=percent
    print '--------', sum_percent

res = {}

for url in urls:
    #print url
    # try:
        
        #print resp.url
    domain = find_domain2(url)

    if domain in res:
        res[domain].append(url)
    else:
        res[domain] = [url]

    #print sorted(res.items(), key=operator.itemgetter(1), reverse=True)
    #print_result(res)
# except (HTTPError, URLError, ) as e:
    #     memo[url] = 'ERROR'
    #     print 'ERROR: ', e, e.__class__

    
#sorted_urls = sorted(res.items(), key=operator.itemgetter(1))
print_result(res)
#print sorted_urls


