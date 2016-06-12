import argparse
import copy
import defaults


ARGUMENTS = {
    'dataset': {'required': True, 'help': 'dataset name'},
    'model': {'required': True, 'help': 'model name'},
    'tweets': {'required': True, 'help': 'name of file with tweets'},
    'dataset_applied': {'required': True, 'help': 'dataset_applied name'},
    'tweets_applied': {'required': True, 'help': 'tweets_applied name'},

    'input_dir': { 'default': defaults.TMP_FILE_DIRECTORY, 'help': 'input directory'},
    'output_dir': {'default': defaults.TMP_FILE_DIRECTORY, 'help': 'output directory'},

    'wtmf': {'action': 'store_true', 'help': 'wtmf method'},
    'wtmf_g': {'action': 'store_true', 'help': 'wtmf_g method'},
    'resolve': {'action': 'store_true', 'help': 'resolve urls from all tweets'},
    'analyze': {'action': 'store_true', 'help': 'print stats of resolved urls'},
    'recommend': {'action': 'store_true', 'help': 'build recomendation'},
    'eval': {'action': 'store_true', 'help': 'eval recomendation results'},
    'dump': {'action': 'store_true', 'help': 'dump recomendation result to file'},
    'print': {'action': 'store_true', 'help': 'print recomendation result to stdout'},

    'unique_words': {'default': 0.0, 'type': float, 'help': 'percent of unique words in tweet by corresponding news'},
    'length': {'default': 10, 'type': int, 'help': 'num of tweets in sample'},
}

PARSER_KWARGS = {'formatter_class': argparse.ArgumentDefaultsHelpFormatter}


def get_arg(name):
    arg = copy.deepcopy(ARGUMENTS[name])
    arg['dest'] = name
    return arg


def add_arg(group, name):
    group.add_argument('--' + name, **get_arg(name))


def add_args(group, names):
    for name in names:
        add_arg(group, name)


def parse_args():
    parser = argparse.ArgumentParser(description='twnews command line interface', **PARSER_KWARGS)
    subparsers = parser.add_subparsers(dest='subparser', help='sub-commands')

    random_tweets_parser = subparsers.add_parser(name='tweets_sample', help='get sample of random tweets', **PARSER_KWARGS)
    add_args(random_tweets_parser, ['length'])

    dataset_parser = subparsers.add_parser('build_dataset', help='construct dataset', **PARSER_KWARGS)
    add_args(dataset_parser, ['unique_words', 'output_dir'])

    resolve_parser = subparsers.add_parser('resolver', help='url resorlver', **PARSER_KWARGS)
    resolve_group = resolve_parser.add_mutually_exclusive_group(required=True)
    add_args(resolve_group, ['resolve', 'analyze'])

    train_parser = subparsers.add_parser('train', help='train model', **PARSER_KWARGS)
    train_group = train_parser.add_mutually_exclusive_group(required=True)
    add_args(train_group, ['wtmf', 'wtmf_g'])
    add_args(train_parser, ['dataset', 'input_dir', 'output_dir'])

    apply_parser = subparsers.add_parser('apply', help='apply WTMF or WTMF-G model', **PARSER_KWARGS)
    apply_group = apply_parser.add_mutually_exclusive_group(required=True)
    add_args(apply_group, ['wtmf', 'wtmf_g'])
    add_args(apply_parser, ['model', 'tweets', 'input_dir', 'output_dir'])

    tfidf_parser = subparsers.add_parser(name='tfidf', help='apply tfidf', **PARSER_KWARGS)
    add_args(tfidf_parser, ['dataset', 'tweets', 'input_dir', 'output_dir'])

    recommendation_parser = subparsers.add_parser('recommendation', help='recommendation', **PARSER_KWARGS)
    recommendation_group = recommendation_parser.add_mutually_exclusive_group(required=True)
    add_args(recommendation_group, ['recommend', 'eval', 'dump', 'print'])
    add_args(recommendation_parser, ['dataset_applied', 'tweets_applied', 'input_dir', 'output_dir'])

    args = parser.parse_args()

    return args
