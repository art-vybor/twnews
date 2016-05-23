import httplib
import socket
import urllib2
from urlparse import urlparse

from twnews.utils.extra import timeit

urls = ['https://t.co/VkVNxPB8IF', 'https://t.co/cAE017IBa1', 'https://t.co/Ke8KMdNuX4', 'https://t.co/oztuA8pfFy',
        'https://t.co/98YuY5aoBu', 'https://t.co/VcJSsbBCUM', 'https://t.co/XmHF5xoGYw', 'https://t.co/EXhvEUqeob']

TIMEOUT = 4
socket.setdefaulttimeout(TIMEOUT)

headers = {'User-Agent': 'Mozilla/5.0'}


def site_open_unshorter(url):
    try:
        req = urllib2.Request(url, None, headers)

        return urllib2.urlopen(req, timeout=TIMEOUT).url
    except Exception as _:
        return None


def header_unshoter(url):
    def good_location(location):
        return location and urlparse(location).netloc and location != url

    parsed = urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc, timeout=TIMEOUT)

    try:        
        h.request('HEAD', parsed.path, headers=headers)
        response = h.getresponse()
    except Exception as e:
        return None    

    location = response.getheader('Location')
    if good_location(location):
        return header_unshoter(location)
    return url


def unshorten_url(url):

    full_url = header_unshoter(url)
    if not full_url:
        full_url = site_open_unshorter(url)
    return full_url


def web_unshoter(url):
    req = urllib2.Request('http://api.unshorten.it/?shortURL={URL}&responseFormat=text&return=both&apiKey=c4VQRAvzfsQCb3zmhYuHIPkwZO64dlmf'.format(URL=url), None, headers)
    try:
        return urllib2.urlopen(req).read()
    except:
        return None


if __name__ == '__main__':
    @timeit
    def time(f, url):
        return f(url)

    for url in urls[:1]:
        # print url, web_unshoter(url)
        #print 'head   %s -> %s' % (url, time(header_unshoter, url))
        print 'site   %s -> %s' % (url, time(site_open_unshorter, url))
        #print 'stable %s -> %s' % (url, time(unshorten_url, url))