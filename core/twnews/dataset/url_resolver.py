import shelve
import logging

from twnews import defaults
from twnews.logs import log_string


class UrlResolver:
    def __init__(self, resolve_url_map_path=defaults.RESOLVE_URL_MAP_PATH):
        logging.info('Start of loading url_map from {PATH}'.format(PATH=resolve_url_map_path))
        self.resolve_url_map = shelve.open(resolve_url_map_path)
        logging.info('Url map successfully loaded')

    def resolve(self, url):
        return self.resolve_url_map.get(url, None)

    def get_domain(self, url):
        pass
