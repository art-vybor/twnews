import os
import logging

from twnews import defaults
from twnews.dataset.storage import TweetsStorage, NewsStorage
from twnews.dataset.url_resolver import UrlResolver
from twnews.dataset.text_to_text_relation import get_text_to_text_relation
from twnews.utils.text_processors import Lemmatizer
from twnews.utils.text_processors import lemmatize_texts, build_tf_idf_matrix
from twnews.utils.memoize import load
from twnews.utils.sparse_math import get_similarity_matrix


class Dataset(object):
    def __init__(self, news_path=defaults.NEWS_PATH,
                       tweets_path=defaults.TWEETS_PATH,
                       resolve_url_map_path=defaults.RESOLVE_URL_MAP_PATH,
                       fraction=defaults.DATASET_FRACTION,
                       init_by_prepared_tweets=None,
                       percent_of_unique_words=0.0):

        self.type = 'auto' if init_by_prepared_tweets is None else 'manual'
        self.news = load('cutted_news_storage')#NewsStorage(news_path)
        self.tweets = TweetsStorage(tweets_path, fraction, init_by_prepared_tweets)
        self.text_to_text_links = None
        self.percent_of_unique_words = percent_of_unique_words

        if self.type == 'auto':
            url_resolver = UrlResolver(resolve_url_map_path)
            self.tweets.resolve_urls(url_resolver)
            self.tweets.filter(self.news)

        print self.tweets.length()
        if self.percent_of_unique_words > 0.0:
            self.tweets.filter_not_unique_tweets(self.news, self.percent_of_unique_words)

        print self.tweets.length()
        self.lemmatized_texts = lemmatize_texts(self.get_texts())
        self.corpus, self.tf_idf_matrix = build_tf_idf_matrix(self.lemmatized_texts)

        logging.info('Dataset {NAME} builded and consist of {NUM_TWEETS} tweets and {NUM_NEWS} news'.format(
            NAME=self.name(),
            NUM_TWEETS=self.tweets.length(),
            NUM_NEWS=self.news.length()))

    def get_texts(self):
        return self.news.get_texts() + self.tweets.get_texts()

    def get_documents(self):
        return self.news.get_documents() + self.tweets.get_documents()


    def init_text_to_text_links(self):
        logging.info('Finding text to text links for {NAME}'.format(NAME=self.name()))
        lemmatizer = Lemmatizer()
        index = 0
        for _news in self.news.get_documents():
            _news.index = index
            index += 1

        for tweet in self.tweets.get_documents():
            tweet.words = lemmatizer.split_text_to_lemmas(tweet.text)
            tweet.index = index
            index += 1

        #print len(tweets), len(news)
        similarity_matrix = get_similarity_matrix(self.get_documents(), self.get_documents(), self.corpus, self.tf_idf_matrix)
        print 'preparation finished'
        self.text_to_text_links = get_text_to_text_relation(self.news.get_documents(), self.tweets.get_documents(), similarity_matrix)

    def name(self):
        return 'dataset_{TYPE}_{UNIQUE_PERCENT}'.format(TYPE=self.type, UNIQUE_PERCENT=self.percent_of_unique_words)
