#Import the necessary methods from tweepy library
from datetime import datetime
import sys
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from secrets import *

error_log = './consumer_error.log'
data = './consumer_data'

error_log_file = open('error_log', 'a')
data_file = open('data', 'a')

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        data_file.write(data + '\n')
        return True

    def on_error(self, status):
        sys.stderr.write(datetime.now() + ': ' + status + '\n')
        error_log_file.write(datetime.now() + ': ' + status + '\n')
        return False
        #print status



#This handles Twitter authetification and the connection to Twitter Streaming API
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
try:
    stream.sample(languages=['ru'])
except Exception as e:
    sys.stderr.write(datetime.now() + ': ' + e + '\n')
    error_log_file.write(datetime.now() + ': ' + e + '\n')


#     #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
#     stream.
#     #stream.filter(track=['python', 'javascript', 'ruby'])


# import tweepy

# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)

# api = tweepy.API(auth)
# print 1
# public_tweets = api.home_timeline()

# for tweet in public_tweets:
#     print tweet.text