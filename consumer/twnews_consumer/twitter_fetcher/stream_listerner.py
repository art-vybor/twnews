import logging
import json
from tweepy.streaming import StreamListener


def parse_tweet(tweet):
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


class TweepyStreamListener(StreamListener):
    def __init__(self, shelve_db):
        super(StreamListener, self).__init__()
        self.shelve_db = shelve_db

    def on_data(self, data):
        with open('/tmp/test.tweets', 'a') as f:
            f.write(data)
        #print data
        # parsed_tweet = parse_tweet(data)
        # if parsed_tweet:
        #     self.data_file.write(parsed_tweet)
        return True

    def on_error(self, status):
        logging.error('TWITTER> ' + status)
        return False
