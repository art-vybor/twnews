import os
import logging


LOG_FILE = '/var/log/twnews.log'
LOG_LEVEL = logging.INFO


TWNEWS_DATA_PATH = '/home/avybornov/twnews_data/'
NEWS_PATH = os.path.join(TWNEWS_DATA_PATH, 'rss')
TWEETS_PATH = os.path.join(TWNEWS_DATA_PATH, 'tweets')
RESOLVE_URL_MAP_PATH= os.path.join(TWNEWS_DATA_PATH, 'resolve_url_map.shelve')
DATASET_PATH = os.path.join(TWNEWS_DATA_PATH, 'dataset')

DATASET_FRACTION = 1.0


TMP_FILE_DIRECTORY = '/tmp'