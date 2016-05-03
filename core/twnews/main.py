import argparse
import logging
import sys

from twnews import defaults
from twnews.dataset.dataset import Dataset
from twnews.resolver import resolve, url_analyse
from twnews.utils.memoize import memo_process
from twnews.utils.text_processors import lemmatize_texts, build_tf_idf_matrix
from twnews.wtmf.wtmf import WTMF

#reload(logging)
logging.basicConfig(
    filename=defaults.LOG_FILE,
    level=defaults.LOG_LEVEL,
    stream=sys.stdout,
    format='%(asctime)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")


def parse_args():
    parser = argparse.ArgumentParser(description='twnews command line interface.')

    pipe_group = parser.add_mutually_exclusive_group(required=True)

    pipe_group.add_argument('--run_pipe', dest='run_pipe', action='store_true', help='start total pipeline of model build and eval')
    pipe_group.add_argument('--resolve', dest='resolve', action='store_true', help='resolve urls from tweets')
    pipe_group.add_argument('--build_dataset', dest='dataset', action='store_true', help='build dataset')
    pipe_group.add_argument('--train_wtmf', dest='train_wtmf', action='store_true', help='train wtmf')
    pipe_group.add_argument('--analyse_urls', dest='analyze_urls', action='store_true', help='analyze resolved urls')

    parser.add_argument('--try_to_load', dest='try_to_load', action='store_true', help='try_to_load flag')

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    if args.train_wtmf:
        dataset = memo_process(lambda: Dataset(fraction=1), 'dataset', try_to_load=args.try_to_load)
        lemmatized_texts = memo_process(lambda: lemmatize_texts(dataset.get_texts()), 'texts', try_to_load=args.try_to_load)
        corpus, tf_idf_matrix = memo_process(lambda: build_tf_idf_matrix(lemmatized_texts), 'tf_idf_corpus', try_to_load=args.try_to_load)
        print len(lemmatized_texts), len(corpus)

        model = WTMF(lemmatized_texts, corpus, tf_idf_matrix, try_to_load=args.try_to_load)
        model.build()

    elif args.resolve:
        resolve(sample_size=None)
    elif args.analyze_urls:
        url_analyse()
    elif args.dataset:
        dataset = memo_process(lambda: Dataset(fraction=1), 'dataset', try_to_load=False)



