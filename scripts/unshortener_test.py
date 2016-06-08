from twnews.resolver.url_unshortener import urls, site_open_unshorter, header_unshoter, web_unshoter, unshorten_url
from twnews.resolver.resolver import get_urls
from twnews.defaults import TWEETS_PATH

from time import time

def test(f, urls, sample_size=1):
    start = time()

    result = map(f, urls)
    errors_count = len(filter(lambda x: x == None, result))

    total_time = time() - start
    time_by_sample = total_time*(sample_size*1.0/len(urls))
    errors_percent = errors_count/len(urls)

    print f.__name__, '%.4fs; %.2f%% ' % (time_by_sample, errors_percent)

links, _ = get_urls(TWEETS_PATH, sample_size=1000*100)
urls = links.keys()[:500]
print 'total %s urls' % len(urls)
#urls = urls[:1]

test(site_open_unshorter, urls)
test(header_unshoter, urls)
test(unshorten_url, urls)
test(web_unshoter, urls)
