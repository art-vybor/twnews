import os
import logging


LOG_FILE = '/var/log/twnews-consumer.log'
LOG_LEVEL = logging.INFO


TWNEWS_DATA_PATH = '/tmp/twnews_data'  # TODO: import from twnes
TWNEWS_LOGS_PATH = os.path.join(TWNEWS_DATA_PATH, 'logs')


RSS_DB_PATH = os.path.join(TWNEWS_LOGS_PATH, 'rss.shelve')
TWEETS_DB_PATH = os.path.join(TWNEWS_LOGS_PATH, 'tweets.shelve')


RSS_FEEDS = {
    'ria': {'rss_url': 'http://ria.ru/export/rss2/index.xml'},
    'lifenews': {'rss_url': 'http://lifenews.ru/xml/feed.xml'},
    'lenta': {'rss_url': 'http://lenta.ru/rss'},
    'rt': {'rss_url': 'https://russian.rt.com/rss'},
    'gazeta': {'rss_url': 'http://www.gazeta.ru/export/rss/index.xml'},
}


TWEETS_LANGUAGES = ['en', 'ru']


