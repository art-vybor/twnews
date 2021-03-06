import os
import logging


LOG_FILE = '/var/log/twnews-consumer.log'
LOG_LEVEL = logging.INFO


TWNEWS_DATA_PATH = '/home/avybornov/tmp_twnews_data'
TWNEWS_LOGS_PATH = os.path.join(TWNEWS_DATA_PATH, 'logs')


RSS_DB_PATH = os.path.join(TWNEWS_LOGS_PATH, 'rss.shelve')
TWEETS_DB_PATH = os.path.join(TWNEWS_LOGS_PATH, 'tweets.shelve')


RSS_FEEDS = {
    'ria': {'rss_url': 'http://ria.ru/export/rss2/index.xml'},
    'lifenews': {'rss_url': 'http://lifenews.ru/xml/feed.xml1'},
    'lenta': {'rss_url': 'http://lenta.ru/rss'},
    'rt': {'rss_url': 'https://russian.rt.com/rss'},
    'gazeta': {'rss_url': 'http://www.gazeta.ru/export/rss/index.xml'},
}

SOCKET_DEFAULT_TIMEOUT = 10

TWEETS_LANGUAGES = ['ru']


