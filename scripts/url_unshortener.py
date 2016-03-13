import httplib
from urlparse import urlparse
import urllib2

urls = ['https://t.co/cAE017IBa1', 'https://t.co/Ke8KMdNuX4', 'https://t.co/oztuA8pfFy', 'https://t.co/98YuY5aoBu', 'https://t.co/VcJSsbBCUM']

# def old_way(url):
#     return urllib2.urlopen(url).url

def unshorten_url(url):
    parsed = urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc, timeout=4)

    try:
        h.request('HEAD', parsed.path)
        response = h.getresponse()
    except Exception as e:
        print 'ERROR: ', e, e.__class__
        return None    
    
    print response.getheaders()
    print '-------'
    if response.getheader('Location') == url:
        return url
    elif response.getheader('Location'):
        return unshorten_url(response.getheader('Location'))

    return url

for url in urls[4:]:
    print '%s -> %s' % (url,unshorten_url(url))