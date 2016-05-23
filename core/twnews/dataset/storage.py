import shelve
import logging

from collections import OrderedDict
from twnews import defaults
from twnews.dataset.texts import Tweet, News, DatasetText
from twnews.utils.text_processors import Lemmatizer


class DocumentsStorage:
    TextClass = DatasetText

    def __init__(self, data_path, fraction=None):
        logging.info('Start of loading storage of {TYPE} from {PATH}'.format(TYPE=self.TextClass.__name__, PATH=data_path))
        data_shelve = shelve.open(data_path)

        keys = sorted(data_shelve.keys())
        if fraction:
            keys = keys[:int(len(keys)*fraction)]

        self.documents = OrderedDict()
        for key in keys:
            self.documents[key] = self.TextClass(data_shelve[key])

        data_shelve.close()

        logging.info('Loading finished')

    def length(self):
        return len(self.documents)

    def get_texts(self):
        return [dataset_text.get_text() for dataset_text in self.get_documents()]

    def get_documents(self):
        return self.documents.values()

    def exists(self, key):
        return key in self.documents

    def get(self, key):
        return self.documents[key]


class TweetsStorage(DocumentsStorage):
    TextClass = Tweet

    def __init__(self, tweets_path=defaults.TWEETS_PATH, fraction=None, init_by_prepared_tweets=None):
        if init_by_prepared_tweets:
            self.documents = OrderedDict()
            for tweet in init_by_prepared_tweets:
                self.documents[tweet.tweet_id] = tweet
        else:
            DocumentsStorage.__init__(self, tweets_path, fraction)

    def resolve_urls(self, url_resolver):
        for tweet in self.documents.itervalues():
            tweet.resolve_urls(url_resolver)

    def filter(self, news_storage):
        for tweet_id, tweet in self.documents.items():
            if not any(map(news_storage.exists, tweet.urls)):
                del self.documents[tweet_id]

    def tweets_unique(self, lemmatizer, tweet, news_storage, percent_of_unique_words):
        tweet_words = lemmatizer.split_text_to_lemmas_without_lemmatize(tweet.text)

        for url in tweet.urls:
            if news_storage.exists(url):
                single_news = news_storage.get(url)
                single_news_words = lemmatizer.split_text_to_lemmas_without_lemmatize(single_news.title)

                unique_words = len([word for word in tweet_words if word not in single_news_words])
                unique_words_normalized = unique_words*1.0/len(tweet_words)
                if unique_words_normalized >= percent_of_unique_words:
                    return True
        return False

    def filter_not_unique_tweets(self, news_storage, percent_of_unique_words):
        lemmatizer = Lemmatizer()
        for tweet_id, tweet in self.documents.items():
            if not self.tweets_unique(lemmatizer, tweet, news_storage, percent_of_unique_words):
                del self.documents[tweet_id]


class NewsStorage(DocumentsStorage):
    TextClass = News

    def __init__(self, news_path=defaults.NEWS_PATH, fraction=None):
        DocumentsStorage.__init__(self, news_path, fraction)

    # def cast_url_to_news_format(self, url):
    #     o = urlparse(url)
    #     return 'http://' + o.netloc + o.path

    def exists(self, key):
        return key in self.documents
