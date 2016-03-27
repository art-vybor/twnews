from dateutil import parser as date_parser
import shelve
import re
import logging

from twnews import defaults
from twnews.logs import log_string
from twnews.dataset.url_resolver import UrlResolver


class Tweet():
    def __init__(self, tweet_row, url_resolver):
        self.parse(tweet_row, url_resolver)        

    def parse(self, tweet_row, url_resolver):
        retweet, date, text = tweet_row.split('\t', 2)
        urls = self.get_all_urls(text)
        for url in urls:
            text = text.replace(url, '')

        self.retweet = bool(retweet)
        self.date = date_parser.parse(date)
        self.text = text
        self.urls = map(url_resolver.resolve, urls)

    def get_all_urls(self, tweet_text):
        return re.findall('https?://t.co/[\w\d]{10}', tweet_text)

    def __str__(self):
        return self.text

    def __repr__(self):
        return 'TWEET: %s' % str(self)


class TweetsStorage():
    def __init__(self, tweets_path=defaults.TWEETS_PATH, resolve_url_map_path=defaults.RESOLVE_URL_MAP_PATH, fraction=None):
        self.url_resolver = UrlResolver(resolve_url_map_path)

        logging.info(log_string('Start of loading and parsing tweets from {PATH}'.format(PATH=tweets_path)))        
        self.tweets_list = self.parse_tweets(tweets_path, fraction)        
        logging.info(log_string('Tweets successfully parsed'))

    def parse_tweets(self, tweets_path, fraction=None):
        tweets_data = None
        with open(tweets_path) as f:
            tweets_data = f.read()

        raw_tweets_list = tweets_data.split('\n')

        if fraction:
            fractioned_top = int(len(raw_tweets_list)*fraction)
            raw_tweets_list = raw_tweets_list[:fractioned_top]

        raw_tweets_list_decoded = [row.decode('string_escape') for row in raw_tweets_list if row]

        return map(lambda row: Tweet(row, self.url_resolver), raw_tweets_list_decoded)

    def length(self):
        return len(self.tweets_list)


class News():
    def __init__(self, news_dict):
        self.source = news_dict['source']
        self.time = news_dict['time']
        self.link = news_dict['link']
        self.summary = news_dict['summary']
        self.title = news_dict['title'].encode('utf-8')

    def __str__(self):
        return self.title

    def __repr__(self):
        return 'NEWS: %s' % str(self)


class NewsStorage():
    def __init__(self, news_path=defaults.NEWS_PATH):
        logging.info(log_string('Start of loading news from {PATH}'.format(PATH=news_path)))
        news_shelve = shelve.open(news_path)
        self.news_dict = {key: News(value) for key, value in news_shelve.iteritems()}
        logging.info(log_string('News successfully loaded'))

    def exists(self, url):
        return url in self.news_dict

    def length(self):
        return len(self.news_dict.keys())

    def get(self, url):
        return self.news_dict[url]

    def get_texts(self):
        texts = []
        for url, news in self.news_dict.iteritems():
            texts.append(news.summary if news.summary else news.title)
        return texts
