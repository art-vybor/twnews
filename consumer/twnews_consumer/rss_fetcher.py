import shelve
import feedparser
import logging
from twnews_consumer import defaults

import socket
socket.setdefaulttimeout(defaults.SOCKET_DEFAULT_TIMEOUT)


class RssFetcher:
    """Read rss feed and put it to shelve database"""

    def __init__(self, rss_feeds=defaults.RSS_FEEDS, db_path=defaults.RSS_DB_PATH):
        self.rss_feeds = rss_feeds
        self.db = shelve.open(db_path)

    def write_news_to_db(self, news_data):
        url = news_data['link'].encode('utf-8')
        if url not in self.db:
            self.db[url] = news_data
            self.db.sync()

    def parse_feed(self, rss_config):
        source, rss_data = rss_config
        feed = feedparser.parse(rss_data['rss_url'])

        for entry in feed.entries:
            summary = entry.summary_detail['value']
            if not summary:
                summary = entry.summary
            entry_data = {
                'summary': summary,
                'link': entry.link,
                'title': entry.title,
                'time': entry.published,
                'source': source
            }
            self.write_news_to_db(entry_data)

    def parse_all_feeds(self):
        for rss_config in self.rss_feeds.iteritems():
            self.parse_feed(rss_config)

    def fetch(self):
        logging.info('RSS> Start consume rss feeds')
        while True:
            try:
                self.parse_all_feeds()
            except KeyboardInterrupt:
                logging.info('RSS> Ctrl-C catched, finalizing')
                return
            except Exception as e:
                logging.error('RSS> {ERROR}'.format(ERROR=str(e)))

