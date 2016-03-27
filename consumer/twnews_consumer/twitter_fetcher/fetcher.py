import logging
import threading
import shelve
import Queue
import marshal

from tweepy import OAuthHandler
from tweepy import Stream

from twnews_consumer import defaults, secrets
from twnews_consumer.twitter_fetcher.stream_listerner import TweepyStreamListener


class TwitterFetcher:
    def __init__(self, languages=defaults.TWEETS_LANGUAGES, db_path=defaults.TWEETS_DB_PATH):
        self.languages = languages
        self.db_path = db_path
        self.shelve_db = shelve.open(self.db_path)
        self.async_queue = Queue.Queue()
        self.killed = False

    def db_writer(self):
        logging.info('TWITTER> Starting write to {FILENAME}'.format(FILENAME=self.db_path))
        while True and not self.killed:
            while not self.async_queue.empty():
                tweet = self.async_queue.get()
                self.shelve_db[str(tweet['id'])] = tweet
                self.shelve_db.sync()

                if self.async_queue.qsize() > 1000:
                    logging.WARNING('TWITTER> result queue looks like too big ({NUM_OF_ELEMENTS} elements)'.
                                    format(NUM_OF_ELEMENTS=self.async_queue.qsize()))

    def fetch(self):
        writer_thread = threading.Thread(target=self.db_writer)
        writer_thread.start()

        logging.info('TWITTER> Starting to consume twitter')
        while True:
            try:
                stream = self.create_tweepy_stream()
                stream.sample()
            except KeyboardInterrupt:
                logging.info('TWITTER> Ctrl-C catched, finalizing')
                self.killed = True
                writer_thread.join()
                return
            except Exception as e:
                logging.error('TWITTER> {ERROR}'.format(ERROR=str(e)))

    def create_tweepy_stream(self):
        # This handles Twitter authentication and the connection to Twitter Streaming API
        l = TweepyStreamListener(self.async_queue)
        auth = OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
        auth.set_access_token(secrets.access_token, secrets.access_token_secret)
        stream = Stream(auth, l)
        return stream
