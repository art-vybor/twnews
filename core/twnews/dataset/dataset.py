import os
import logging

from twnews import defaults
from twnews.dataset.storage import TweetsStorage, NewsStorage
from twnews.dataset.url_resolver import UrlResolver


class Dataset(object):
    def __init__(self, news_path=defaults.NEWS_PATH,
                       tweets_path=defaults.TWEETS_PATH,
                       resolve_url_map_path=defaults.RESOLVE_URL_MAP_PATH,
                       fraction=defaults.DATASET_FRACTION):

        self.news = NewsStorage(news_path)
        self.tweets = TweetsStorage(tweets_path, resolve_url_map_path, fraction)
        url_resolver = UrlResolver(resolve_url_map_path)
        self.tweets.resolve_urls(url_resolver)
        self.tweets.filter(self.news)

        logging.info('Dataset builded and consist of {NUM_TWEETS} tweets and {NUM_NEWS} news'.format(
            NUM_TWEETS=self.tweets.length(),
            NUM_NEWS=self.news.length()))

