#!/usr/bin/python

import os
import time
from datetime import datetime

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from secrets import *
import defaults

import logging
logging.basicConfig(filename=defaults.log_file, level=logging.INFO)


def log_string(message):
    return '{DATE}: {MESSAGE}'.format(DATE=datetime.utcnow(), MESSAGE=message)


def timestamp_ms():
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()*1000)


class StdOutListener(StreamListener):

    def __init__(self, data_file):
        super(StreamListener, self).__init__()
        self.data_file = data_file

    def on_data(self, data):
        self.data_file.write(data)
        return True

    def on_error(self, status):
        logging.error(log_string(status))
        return False


while True:
    data_filename = os.path.join(defaults.data_directory, str(timestamp_ms()))

    with open(data_filename, mode='a') as data_file:
        logging.info(log_string('Starting write to {FILENAME}'.format(FILENAME=data_filename)))
        try:
            #This handles Twitter authetification and the connection to Twitter Streaming API
            l = StdOutListener(data_file)
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            stream = Stream(auth, l)
            stream.sample()
        except Exception as e:
            logging.error(log_string(e))
