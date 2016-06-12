import argparse



ARGUMENTS = {
    'some_arg' : ''
}


def parse_args():
    parser = argparse.ArgumentParser(description='twnews command line interface.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #subparsers = parser.add_subparsers(dest='subparser_name', help='sub-commands')
    argument = {'dest':'--build_automatic', 'dest': 'automatic', 'action':'store_true', 'help':'build automatic dataset'}

    parser.add_argument(**argument)

    # dataset_parser = subparsers.add_parser('dataset', help='construct dataset')
    # dataset_group = dataset_parser.add_mutually_exclusive_group(required=True)
    # dataset_group.add_argument('--build_automatic', dest='automatic', action='store_true', help='build automatic dataset')
    # dataset_group.add_argument('--build_manual', dest='manual', action='store_true', help='build manual dataset')
    # dataset_parser.add_argument('--unique_words_in_tweet', dest='percent_of_unique_words', default=0.0, type=float, help='percent of unique words in tweet by corresponding news')
    #
    # train_parser = subparsers.add_parser('train', help='train model')
    # train_group = train_parser.add_mutually_exclusive_group(required=True)
    # train_group.add_argument('--wtmf', dest='wtmf', action='store_true', help='train wtmf model')
    # train_group.add_argument('--wtmf_g', dest='wtmf_g', action='store_true', help='train wtmf-g model')
    # train_group.add_argument('--tfidf', dest='tfidf', action='store_true', help='train tfidf model')
    # train_parser.add_argument('--try_to_load', dest='try_to_load', action='store_true', help='try_to_load flag')
    # train_parser.add_argument('--dataset_file', dest='dataset_file', help='load dataset from file')
    #
    # apply_parser = subparsers.add_parser('apply', help='apply model')
    # apply_group = apply_parser.add_mutually_exclusive_group(required=True)
    # apply_group.add_argument('--wtmf', dest='wtmf', action='store_true', help='apply wtmf model')
    # apply_group.add_argument('--wtmf_g', dest='wtmf_g', action='store_true', help='apply wtmf-g model')
    # apply_group.add_argument('--tfidf', dest='tfidf', action='store_true', help='apply tfidf model')
    #
    # resolve_parser = subparsers.add_parser('resolver', help='url resorlver')
    # resolve_group = resolve_parser.add_mutually_exclusive_group(required=True)
    # resolve_group.add_argument('--resolve', dest='resolve', action='store_true', help='resolve urls from all tweets')
    # resolve_group.add_argument('--analyze', dest='analyze', action='store_true', help='print stats of resolved urls')
    #
    # recommend_parser = subparsers.add_parser('recommend', help='recommendation')
    # reccomend_group = recommend_parser.add_mutually_exclusive_group(required=True)
    # reccomend_group.add_argument('--recommend', dest='recommend', action='store_true', help='build recomendation')
    # reccomend_group.add_argument('--recommend_by_model', dest='recommend_by_model', help='recommend on dev set for prebuilded model')
    # reccomend_group.add_argument('--eval', dest='eval', action='store_true', help='eval recomendation result')
    # reccomend_group.add_argument('--dump_to_csv', dest='dump_to_csv', action='store_true', help='dump recommendation to csv')

    args = parser.parse_args()

    return args