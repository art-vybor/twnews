import shelve
import logging

from tweepy import OAuthHandler
from tweepy import Stream

from twnews_consumer import defaults
from twnews_consumer import secrets
from twnews_consumer.twitter_fetcher.stream_listerner import TweepyStreamListener


class TwitterFetcher:
    def __init__(self, languages=defaults.TWEETS_LANGUAGES, db_path=defaults.TWEETS_DB_PATH):
        self.languages = languages
        self.db_path = db_path
        self.shelve_db = shelve.open(self.db_path)

    def fetch(self):
        while True:
            #with open(data_filename, mode='a') as data_file:
            logging.info('TWITTER> Starting write to {FILENAME}'.format(FILENAME=self.db_path))
            try:
                stream = self.create_tweepy_stream()
                stream.sample()
            except Exception as e:
                logging.error('TWITTER> {ERROR}'.format(ERROR=str(e)))

    def create_tweepy_stream(self):
        #This handles Twitter authetification and the connection to Twitter Streaming API
        l = TweepyStreamListener(self.shelve_db)
        auth = OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
        auth.set_access_token(secrets.access_token, secrets.access_token_secret)
        stream = Stream(auth, l)
        return stream
