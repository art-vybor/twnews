import json
import os
import time
import logging
from datetime import datetime

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from twnews_consumer import defaults
from twnews_consumer.logs import log_string
from twnews_consumer.secrets import *


class StdOutListener(StreamListener):

    def __init__(self, data_file):
        super(StreamListener, self).__init__()
        self.data_file = data_file

    def on_data(self, data):
        parsed_tweet = self.parse_tweet(data)
        if parsed_tweet:
            self.data_file.write(parsed_tweet)
        return True

    def on_error(self, status):
        logging.error(log_string('TWITTER> ' + status))
        return False


    def parse_tweet(self, tweet):
        parsed_tweet = json.loads(tweet)

        if 'delete' not in parsed_tweet:        
            lang = parsed_tweet['lang']        
            if lang in ['ru']:
                retweet = False
                text = parsed_tweet['text']
                if 'retweeted_status' in parsed_tweet: #tweet retweeted
                    text = parsed_tweet['retweeted_status']['text']
                    retweet = True
                text = text.encode('utf8').encode('string-escape')
                created_at = parsed_tweet['created_at']
                #time_ms = float(parsed_tweet['timestamp_ms'])/1000

                return '%s\t%s\t%s\n' % (retweet, created_at, text)

def consume_tweets():
    while True:
        data_filename = defaults.TWEETS_DATA_PATH

        with open(data_filename, mode='a') as data_file:
            logging.info(log_string('TWITTER> Starting write to {FILENAME}'.format(FILENAME=data_filename)))
            try:
                #This handles Twitter authetification and the connection to Twitter Streaming API
                l = StdOutListener(data_file)
                auth = OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_token_secret)
                stream = Stream(auth, l)
                #stream.sample()
                stream.sample()
            except Exception as e:
                logging.error(log_string('TWITTER> {ERROR}'.format(ERROR=str(e))))
