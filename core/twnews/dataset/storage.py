import shelve
import logging
from urlparse import urlparse
from collections import OrderedDict
from twnews import defaults
from twnews.dataset.texts import Tweet, News, DatasetText


class DatasetTextsStorage:
    TextClass = DatasetText

    def __init__(self, data_path, fraction=None):
        logging.info('Start of loading storage of {TYPE} from {PATH}'.format(TYPE=self.TextClass.__name__, PATH=data_path))
        data_shelve = shelve.open(data_path)

        keys = sorted(data_shelve.keys())
        if fraction:
            keys = keys[:int(len(keys)*fraction)]

        self.dataset_texts_dict = OrderedDict()
        for key in keys:
            self.dataset_texts_dict[key] = self.TextClass(data_shelve[key])

        data_shelve.close()

        logging.info('Loading finished')

    def length(self):
        return len(self.dataset_texts_dict)

    def get_texts(self):
        return [dataset_text.get_text() for dataset_text in self.get_dataset_texts()]

    def get_dataset_texts(self):
        return self.dataset_texts_dict.values()

    def exists(self, key):
        return key in self.dataset_texts_dict

    def get(self, key):
        return self.dataset_texts_dict[key]


class TweetsStorage(DatasetTextsStorage):
    TextClass = Tweet

    def __init__(self, tweets_path=defaults.TWEETS_PATH, fraction=None, init_by_prepared_tweets=None):
        if init_by_prepared_tweets:
            self.dataset_texts_dict = {}
            for tweet in init_by_prepared_tweets:
                self.dataset_texts_dict[tweet.tweet_id] = tweet

        else:
            DatasetTextsStorage.__init__(self, tweets_path, fraction)

    def resolve_urls(self, url_resolver):
        for tweet in self.dataset_texts_dict.itervalues():
            tweet.resolve_urls(url_resolver)

    def filter(self, news_storage):
        for tweet_id, tweet in self.dataset_texts_dict.items():
            if not any(map(news_storage.exists, tweet.urls)):
                del self.dataset_texts_dict[tweet_id]


class NewsStorage(DatasetTextsStorage):
    TextClass = News

    def __init__(self, news_path=defaults.NEWS_PATH, fraction=None):
        DatasetTextsStorage.__init__(self, news_path, fraction)

    # def cast_url_to_news_format(self, url):
    #     o = urlparse(url)
    #     return 'http://' + o.netloc + o.path

    def exists(self, key):
        return key in self.dataset_texts_dict
