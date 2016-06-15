import os
import argparse
import copy
from twnews import defaults

ARGUMENTS = {
    'dataset': {'default': os.path.join(defaults.TMP_FILE_DIRECTORY, 'dataset'), 'help': 'dataset filepath'},
    'model': {'default': os.path.join(defaults.TMP_FILE_DIRECTORY, 'WTMF_(dataset_auto_0.0)_90_1_1.95_0.95'), 'help': 'model filepath'},
    'tweets': {'default': os.path.join(defaults.TMP_FILE_DIRECTORY, 'tweets_sample'), 'help': 'tweets sample filepath'},

    'model_dir': {'default': os.path.join(defaults.TMP_FILE_DIRECTORY), 'help': 'name of directory to save model'},

    'dataset_applied': {'default': os.path.join(defaults.TMP_FILE_DIRECTORY, 'dataset_applied'), 'help': 'dataset_applied filepath'},
    'tweets_applied': {'default': os.path.join(defaults.TMP_FILE_DIRECTORY, 'tweets_applied'), 'help': 'tweets_applied filepath'},
    'file': {'default': os.path.join(defaults.TMP_FILE_DIRECTORY, 'reccommendation_dump'), 'help': 'recommendation dump filepath'},


    'wtmf': {'action': 'store_true', 'help': 'wtmf method'},
    'wtmf_g': {'action': 'store_true', 'help': 'wtmf_g method'},
    'resolve': {'action': 'store_true', 'help': 'resolve urls from all tweets'},
    'analyze': {'action': 'store_true', 'help': 'print stats of resolved urls'},
    'evaluate': {'action': 'store_true', 'help': 'eval recomendation results'},
    'dump': {'action': 'store_true', 'help': 'dump recomendation result to file'},

    'unique_words': {'default': 0.0, 'type': float, 'help': 'percent of unique words in tweet by corresponding news'},
    'length': {'default': 1000, 'type': int, 'help': 'num of tweets in sample'},
}

PARSER_KWARGS = {'formatter_class': argparse.ArgumentDefaultsHelpFormatter}


def get_arg(name):
    arg = copy.deepcopy(ARGUMENTS[name])
    if not 'dest' in arg:
        arg['dest'] = name
    return arg


def add_arg(group, name):
    arg = get_arg(name)
    group.add_argument('--' + arg['dest'], **arg)


def add_args(group, names):
    for name in names:
        add_arg(group, name)


def parse_args():
    parser = argparse.ArgumentParser(description='twnews command line interface', **PARSER_KWARGS)
    subparsers = parser.add_subparsers(dest='subparser', help='sub-commands')

    random_tweets_parser = subparsers.add_parser(name='tweets_sample', help='get sample of random tweets', **PARSER_KWARGS)
    add_args(random_tweets_parser, ['length', 'tweets'])

    resolve_parser = subparsers.add_parser('resolver', help='url resorlver', **PARSER_KWARGS)
    resolve_group = resolve_parser.add_mutually_exclusive_group(required=True)
    add_args(resolve_group, ['resolve', 'analyze'])

    dataset_parser = subparsers.add_parser('build_dataset', help='construct dataset', **PARSER_KWARGS)
    add_args(dataset_parser, ['unique_words', 'dataset'])

    train_parser = subparsers.add_parser('train', help='train model', **PARSER_KWARGS)
    train_group = train_parser.add_mutually_exclusive_group(required=True)
    add_args(train_group, ['wtmf', 'wtmf_g'])
    add_args(train_parser, ['dataset', 'model_dir', 'dataset_applied'])

    apply_parser = subparsers.add_parser('apply', help='apply WTMF or WTMF-G model', **PARSER_KWARGS)
    apply_group = apply_parser.add_mutually_exclusive_group(required=True)
    add_args(apply_group, ['wtmf', 'wtmf_g'])
    add_args(apply_parser, ['model', 'tweets', 'tweets_applied'])

    tfidf_parser = subparsers.add_parser(name='tfidf_dataset', help='apply tfidf to dataset', **PARSER_KWARGS)
    add_args(tfidf_parser, ['dataset', 'dataset_applied'])

    tfidf1_parser = subparsers.add_parser(name='tfidf_tweets', help='apply tfidf to tweets', **PARSER_KWARGS)
    add_args(tfidf1_parser, ['dataset', 'dataset_applied', 'tweets', 'tweets_applied'])

    recommendation_parser = subparsers.add_parser('recommendation', help='work with recommendation', **PARSER_KWARGS)
    recommendation_group = recommendation_parser.add_mutually_exclusive_group(required=True)
    add_args(recommendation_group, ['evaluate', 'dump'])
    add_args(recommendation_parser, ['dataset_applied', 'tweets_applied', 'file'])

    args = parser.parse_args()
    return args
