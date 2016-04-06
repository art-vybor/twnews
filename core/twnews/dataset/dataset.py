import os
import logging
import pickle

from twnews import defaults
from twnews.dataset.storage import TweetsStorage, NewsStorage
from twnews.logs import log_string


class Dataset(object):
    def __init__(self, news_path=defaults.NEWS_PATH,
                       tweets_path=defaults.TWEETS_PATH,
                       resolve_url_map_path=defaults.RESOLVE_URL_MAP_PATH,
                       fraction=defaults.DATASET_FRACTION,
                       dataset_path=defaults.DATASET_PATH,
                       use_dataset_if_exist=False):
        self.dataset_path = dataset_path
        self.news_path = news_path
        self.dataset = []
        if use_dataset_if_exist and os.path.isfile(self.dataset_path):
            self.load()
        else:
            self.news_storage = NewsStorage(news_path)
            self.tweets_storage = TweetsStorage(tweets_path, resolve_url_map_path, fraction)
            self.build()


    def build(self):
        logging.info(log_string('Start building dataset from {NUM_TWEETS} tweets and {NUM_NEWS} news'.format(
            NUM_TWEETS=self.tweets_storage.length(),
            NUM_NEWS=self.news_storage.length(),
        )))

        for tweet in self.tweets_storage.tweets_list:
            for url in tweet.urls:
                if self.news_storage.exists(url):
                    self.dataset.append(tweet)
        logging.info(log_string('Dataset builded and consist {NUM_TWEETS} tweets'.format(NUM_TWEETS=len(self.dataset))))

        self.save()

    def save(self):
        with open(self.dataset_path, 'wb') as dataset_file:
            pickle.dump(self.dataset, dataset_file)

    def load(self):
        with open(self.dataset_path, 'rb') as dataset_file:
            self.dataset = pickle.load(dataset_file)
            self.news_storage = NewsStorage(self.news_path)
