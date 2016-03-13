import logging


LOG_FILE = '/var/log/twnews-consumer.log'
LOG_LEVEL = logging.INFO


RSS_FEEDS = {
    'ria': {'rss_url': 'http://ria.ru/export/rss2/index.xml'},
    'lifenews': {'rss_url': 'http://lifenews.ru/xml/feed.xml'}
}
RSS_DB_PATH = '/home/avybornov/logs/rss'

TWEETS_DATA_PATH = '/home/avybornov/logs/tweets'#'/mnt/yandex.disk/logs/twitter'