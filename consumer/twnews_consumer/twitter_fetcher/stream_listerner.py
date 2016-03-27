import logging
import json
from tweepy.streaming import StreamListener
from twnews_consumer import defaults


def parse_tweet(tweet_text):
    tweet = json.loads(tweet_text)
    if 'delete' not in tweet:
        # info about base_tweet
        created_at = tweet['created_at']
        tweet_id = tweet['id']
        retweeted = 'retweeted_status' in tweet

        # go deeper :-)
        while 'retweeted_status' in tweet:
            tweet = tweet['retweeted_status']

        # info about dest tweet
        lang = tweet['lang']
        entities = tweet['entities']
        text = tweet['text']

        if lang in defaults.TWEETS_LANGUAGES:
            # extract links and media links
            media_links = {}
            if 'media' in entities:
                for media in entities['media']:
                    media_links[media['url']] = media['expanded_url']
            links = {}
            if 'urls' in entities:
                for url in entities['urls']:
                    links[url['url']] = url['expanded_url']

            # extract hastags
            hashtags = {}
            if 'hashtags' in tweet['entities']:
                for hashtag in tweet['entities']['hashtags']:
                    hashtags[hashtag['text']] = hashtag['indices']

            # remove url of all links from the text
            #print 'media: %s, links: %s' % (media_links.keys(),links.keys())
            for url in media_links.keys() + links.keys():
                text = text.replace(url, '')

            return {
                'id': tweet_id,
                'retweeted': retweeted,
                'created_at': created_at,
                'lang': lang,
                'text': text,
                'links': links,
                'media_links': media_links,
                'hashtags': hashtags
            }


class TweepyStreamListener(StreamListener):
    def __init__(self, result_queue):
        super(StreamListener, self).__init__()
        self.result_queue = result_queue

    def on_data(self, data):
        tweet = parse_tweet(data)
        if tweet:
            self.result_queue.put(tweet)
        return True

    def on_error(self, status):
        logging.error('TWITTER> ' + status)
        return False
