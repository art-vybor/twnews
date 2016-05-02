from dateutil import parser as date_parser
from twnews.resolver import clean_url

class DatasetText:
    text = None

    def get_text(self):
        return self.text


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
        return self.text

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