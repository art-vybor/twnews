import os
import logging

from twnews import defaults
from twnews.dataset.storage import TweetsStorage, NewsStorage
from twnews.dataset.url_resolver import UrlResolver
from twnews.dataset.text_to_text_relation import get_text_to_text_relation
from twnews.utils.text_processors import Lemmatizer


class Dataset(object):
    def __init__(self, news_path=defaults.NEWS_PATH,
                       tweets_path=defaults.TWEETS_PATH,
                       resolve_url_map_path=defaults.RESOLVE_URL_MAP_PATH,
                       fraction=defaults.DATASET_FRACTION,
                       init_by_prepared_tweets=None,
                       percent_of_unique_words=1.0):

        self.news = NewsStorage(news_path)
        self.tweets = TweetsStorage(tweets_path, fraction, init_by_prepared_tweets)
        self.text_to_text_links = None
        if not init_by_prepared_tweets:
            url_resolver = UrlResolver(resolve_url_map_path)
            self.tweets.resolve_urls(url_resolver)
            self.tweets.filter(self.news)

        if percent_of_unique_words < 1.0:
            self.tweets.filter_not_unique_tweets(self.news, percent_of_unique_words)

        #self.tweets.
        logging.info('Dataset builded and consist of {NUM_TWEETS} tweets and {NUM_NEWS} news'.format(
            NUM_TWEETS=self.tweets.length(),
            NUM_NEWS=self.news.length()))

    def get_texts(self):
        return self.news.get_texts() + self.tweets.get_texts()

    def get_dataset_texts(self):
        return self.news.get_dataset_texts() + self.tweets.get_dataset_texts()

    def init_text_to_text_links(self):
        lemmatizer = Lemmatizer()
        index = 0
        for _news in self.news.get_dataset_texts():
            _news.index = index
            index += 1

        for tweet in self.tweets.get_dataset_texts():
            tweet.words = lemmatizer.split_text_to_lemmas(tweet.text)
            tweet.index = index
            index += 1

        #print len(tweets), len(news)
        self.text_to_text_links = get_text_to_text_relation(self.news.get_dataset_texts()[:100], self.tweets.get_dataset_texts()[:100])



