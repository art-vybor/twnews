import argparse
import logging
import sys

from twnews_consumer import defaults
from twnews_consumer.rss_fetcher import RssFetcher
from twnews_consumer.twitter_fetcher.fetcher import TwitterFetcher

reload(logging)
logging.basicConfig(
    filename=defaults.LOG_FILE,
    level=defaults.LOG_LEVEL,
    #stream=sys.stdout,
    format='%(asctime)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")


def parse_args():
    parser = argparse.ArgumentParser(description='twnews consumer command line interface.')
    # parser.add_argument('download', choices=['news','tweets'])
    subparsers = parser.add_subparsers(dest='subparser_name', help='sub-commands')

    download_parser = subparsers.add_parser('download', help='consume news or tweets data')
    group = download_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--news', action='store_true', help='start downloading news')
    group.add_argument('--tweets', action='store_true', help='start downloading tweets')

    read_parser = subparsers.add_parser('read', help='read news or tweets data')
    group = read_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--news', action='store_true', help='read news data')
    group.add_argument('--tweets', action='store_true', help='read tweets data')
    

    # parser.add_argument('-i', metavar='filename', dest='input_file', required=True, help='input file')
    # parser.add_argument('-o', metavar='filename', dest='output_file', required=False,
    #                     help='output file (default: input_file with rkt extension)')
    # parser.add_argument('--run', action='store_true', help='execute output_file')

    # group = parser.add_argument_group('debug mode')
    # group.add_argument('--stack_trace', action='store_true', help='enable stack trace printing')
    # group.add_argument('--lexems', action='store_true', help='print lexems')
    # group.add_argument('--console_tree', action='store_true', help='print ast tree to console')
    # group.add_argument('--pdf_tree', action='store_true', help='print ast tree to pdf')
    
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    # print args

    if args.subparser_name == 'download':
        if args.news:
            rss_fetcher = RssFetcher()
            rss_fetcher.fetch()
        elif args.tweets:
            twitter_fetcher = TwitterFetcher()
            twitter_fetcher.fetch()


