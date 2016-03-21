import shelve

news_file = '/home/avybornov/twnews_data/rss'
tweets_file = '/home/avybornov/twnews_data/tweets'

# open
shelve.open(news_file)