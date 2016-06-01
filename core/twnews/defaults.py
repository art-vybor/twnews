import os
import logging


LOG_FILE = '/var/log/twnews.log'
LOG_LEVEL = logging.INFO


TWNEWS_DATA_PATH = '/home/avybornov/twnews_data_april/'
#TWNEWS_DATA_PATH = '/home/avybornov/git/twnews/data_sample'
NEWS_PATH = os.path.join(TWNEWS_DATA_PATH, 'rss.shelve')
TWEETS_PATH = os.path.join(TWNEWS_DATA_PATH, 'tweets_filtered.shelve')
RESOLVE_URL_MAP_PATH= os.path.join(TWNEWS_DATA_PATH, 'resolve_url_map.shelve')
DATASET_PATH = os.path.join(TWNEWS_DATA_PATH, 'dataset')

DATASET_FRACTION = 1.0


TMP_FILE_DIRECTORY = '/home/avybornov/tmp'


DEFAULT_WTMF_OPTIONS = {
    'DIM': 90,
    'WM': 0.95,
    'ITERATIONS': 1,
    'LAMBDA': 1.95
}

DEFAULT_WTMFG_OPTIONS = {
    'DIM': 90,
    'WM': 0.95,
    'ITERATIONS': 1,
    'LAMBDA': 1.95,
    'DELTA': 0.1
}
