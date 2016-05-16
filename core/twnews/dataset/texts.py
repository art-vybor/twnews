from dateutil import parser as date_parser
from twnews.resolver import clean_url
import math
from scipy import sparse
import numpy as np

# def cosine_similarity(v1,v2):
#     "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
#     sumxx, sumxy, sumyy = 0, 0, 0
#     for i in range(len(v1)):
#         x = v1[i]; y = v2[i]
#         sumxx += x*x
#         sumyy += y*y
#         sumxy += x*y
#     return sumxy/math.sqrt(sumxx*sumyy)

def cosine_similarity(v1,v2):
    """fast cosine similarity for sparse vectors"""

    v1_idxs, _, value = sparse.find(v1)
    v2_idxs, _, value = sparse.find(v2)

    sumxx, sumxy, sumyy = 0, 0, 0
    for i in set(np.append(v1_idxs, v2_idxs)):
        x = v1[(i,0)]; y = v2[(i,0)]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)


class DatasetText:
    text = None
    date = None
    compare_vector = None  # np vector which represent a text
    # lemmatized_words = None  # lemmatize and filtered words of text
    # text_to_text_link = None  # link

    def get_text(self):
        return self.text

    def set_compare_vector(self, vector):
        self.compare_vector = vector

    def compare(self, obj):
        return cosine_similarity(self.compare_vector, obj.compare_vector)


class Tweet(DatasetText):
    def __init__(self, tweet_dict):
        self.tweet_id = tweet_dict['id']
        self.date = date_parser.parse(tweet_dict['created_at'])
        self.hastags = tweet_dict['hashtags']
        self.urls = map(str, tweet_dict['links'].keys())
        self.retweet = tweet_dict['retweeted']
        self.text = tweet_dict['text']
        # self.lang = tweet_dict['lang']
        # self.media_links = tweet_dict['media_links']

    def resolve_urls(self, url_resolver):
        self.urls = [url_resolver.resolve(url) for url in self.urls]
        self.urls = filter(None, self.urls)
        self.urls = map(clean_url, self.urls)

    def __str__(self):
        return self.text.encode('utf-8')

    def __repr__(self):
        return 'TWEET: %s' % str(self)


class News(DatasetText):
    def __init__(self, news_dict):
        self.link = news_dict['link']
        self.source = news_dict['source']
        self.date = date_parser.parse(news_dict['time'])
        self.summary = news_dict['summary']
        self.title = news_dict['title']#.encode('utf-8')

        title = self.title if self.title else ''
        summary = self.summary if self.summary else ''
        self.text = u'{TITLE} {SUMMARY}'.format(TITLE=title, SUMMARY=summary)

    def __str__(self):
        return self.title.encode('utf-8')

    def __repr__(self):
        return 'NEWS: %s' % str(self)