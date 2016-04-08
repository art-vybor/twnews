import httplib
from urlparse import urlparse
import urllib2

urls = ['https://t.co/cAE017IBa1', 'https://t.co/Ke8KMdNuX4', 'https://t.co/oztuA8pfFy', 'https://t.co/98YuY5aoBu', 'https://t.co/VcJSsbBCUM', 'https://t.co/XmHF5xoGYw', 
    'https://t.co/EXhvEUqeob']

TIMEOUT=4

headers = { 'User-Agent' : 'Mozilla/5.0' }

def site_open_unshorter(url):
    
    try:
        req = urllib2.Request(url, None, headers)
        return urllib2.urlopen(req, timeout=TIMEOUT).url
    except Exception as e:
        #print 'ERROR site: ', url, e, e.__class__
        return None

def header_unshoter(url):
    def good_location(location):
        return location and urlparse(location).netloc and location != url

    #print url
    parsed = urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc, timeout=TIMEOUT)
    

    try:        
        h.request('HEAD', parsed.path, headers=headers)
        response = h.getresponse()
    except Exception as e:
        #print 'ERROR HEAD: ', url, e, e.__class__
        return None    
    
    #print response.getheaders()
    #print '-------'
    location = response.getheader('Location')
    if good_location(location):
        return header_unshoter(location)
    return url


def unshorten_url(url):

    full_url = header_unshoter(url)
    if not full_url:
        full_url = site_open_unshorter(url)
    return full_url



query = 'http://api.unshorten.it/%s'
def web_unshoter(url):
    headers = { 'User-Agent' : 'Mozilla/5.0' }

    req = urllib2.Request('http://api.unshorten.it/?shortURL={URL}&responseFormat=text&return=both&apiKey=c4VQRAvzfsQCb3zmhYuHIPkwZO64dlmf'.format(URL=url), None, headers)
    try:
        return urllib2.urlopen(req).read()
    except:
        return None


if __name__ == '__main__':
    for url in urls[:]:
        #print url, web_unshoter(url)
        #print 'stable %s -> %s' % (url,unshorten_url(url))
        print 'head   %s -> %s' % (url,header_unshoter(url))
        print 'site   %s -> %s' % (url,site_open_unshorter(url))
        # print '--------------------------'


    