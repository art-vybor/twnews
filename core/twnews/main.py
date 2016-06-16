import argparse
import logging
import os
import sys

from twnews import defaults
from twnews.dataset.dataset import Dataset
from twnews.evaluation import RR, TOP1, TOP3
from twnews.model.wtmf import WTMF
from twnews.model.wtmf_g import WTMF_G
from twnews.recommend import recommend, set_compare_vector, dump_to_csv
from twnews.resolver.resolver import resolve
from twnews.resolver.analyze import url_analyse
from twnews.utils.logger_wrapper import log_and_print
from twnews.utils.memoize import load, dump
from twnews.cli import parse_args
from twnews.dataset.storage import TweetsStorage
from twnews.utils.text_processors import lemmatize_texts, build_tf_idf_matrix

# suppress scipy warning
import warnings
from scipy.sparse import SparseEfficiencyWarning

warnings.simplefilter('ignore', SparseEfficiencyWarning)


logging.basicConfig(
    filename=defaults.LOG_FILE,
    level=defaults.LOG_LEVEL,
    stream=sys.stdout,
    format='%(asctime)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")


def split_filepath(filepath):
    return os.path.dirname(filepath), os.path.basename(filepath)


def main():
    args = parse_args()

    logging.info('--------------- Twnews started ------------------')

    if args.subparser == 'tweets_sample':
        log_and_print(logging.INFO, 'get sample of random tweets')
        length = args.length
        tweets_filepath = args.tweets
        tweets_dirname, tweets_filename = split_filepath(tweets_filepath)

        storage = TweetsStorage(defaults.TWEETS_PATH, num_of_documents=length, sorted_keys=False)

        dump(storage.get_documents(), tweets_filename, tweets_dirname)
        # with open(tweets_filepath, 'w') as f:
        #     for doc in storage.get_documents():
        #         f.write('{ID} {TEXT}\n'.format(ID=doc.tweet_id, TEXT=str(doc).replace('\n',' ')))

        log_and_print(logging.INFO, 'sample generated and saved at {PATH}'.format(PATH=tweets_filepath))

    elif args.subparser == 'resolver':
        log_and_print(logging.INFO, 'url resolver')

        if args.resolve:
            log_and_print(logging.INFO, 'resolve all urls')
            resolve(sample_size=None)
            log_and_print(logging.INFO, 'all urls resolved')
        elif args.analyze:
            log_and_print(logging.INFO, 'stats of resolved urls')
            url_analyse()

    elif args.subparser == 'build_dataset':
        log_and_print(logging.INFO, 'building automatic dataset')
        dataset_filepath = args.dataset
        dataset_dirname, dataset_filename = split_filepath(dataset_filepath)
        unique_words = args.unique_words

        dataset = Dataset(fraction=1, percent_of_unique_words=unique_words)
        dataset.init_text_to_text_links()

        dump(dataset, dataset_filename, dataset_dirname)

        log_and_print(logging.INFO, 'dataset builded and saved at {PATH}'.format(PATH=dataset_filepath))

    elif args.subparser == 'train':
        log_and_print(logging.INFO, 'train model')
        dataset_filepath = args.dataset
        dataset_dirname, dataset_filename = split_filepath(dataset_filepath)
        dataset_applied_filepath = args.dataset_applied
        dataset_applied_dirname, dataset_applied_filename = split_filepath(dataset_applied_filepath)
        model_dirname = args.model_dir

        dataset = load(dataset_filename, dataset_dirname)

        if args.wtmf:
            model = WTMF(dataset, dirname=model_dirname)
        elif args.wtmf_g:
            model = WTMF_G(dataset, dirname=model_dirname)

        #log_and_print(logging.INFO, 'train {NAME} model'.format(NAME=model.name()))
        model.build()
        #log_and_print(logging.INFO, 'model {NAME} builded'.format(NAME=model.name()))
        #log_and_print(logging.INFO, 'model saved: {PATH}'.format(PATH=os.path.join(model_dirname, model.name())))

        dump(model.dataset_applied, dataset_applied_filename, dataset_applied_dirname)
        log_and_print(logging.INFO, 'applied dataset saved: {PATH}'.format(PATH=dataset_applied_filepath))

    elif args.subparser == 'apply':
        log_and_print(logging.INFO, 'apply model')
        model_filepath = args.model
        model_dirname, model_filename = split_filepath(model_filepath)
        tweets_filepath = args.tweets
        tweets_dirname, tweets_filename = split_filepath(tweets_filepath)
        tweets_applied_filepath = args.tweets_applied
        tweets_applied_dirname, tweets_applied_filename = split_filepath(tweets_applied_filepath)

        if args.wtmf:
            model = WTMF(model_name=model_filename, dirname=model_dirname)
        elif args.wtmf_g:
            model = WTMF_G(model_name=model_filename, dirname=model_dirname)

        tweets = load(tweets_filename, tweets_dirname)

        corpus = model.words

        texts = map(lambda x: x.get_text(), tweets)
        texts = lemmatize_texts(texts)
        _, tf_idf_matrix = build_tf_idf_matrix(texts, vocabulary=corpus)

        model.texts = texts
        model.tf_idf_matrix = tf_idf_matrix
        result_matrix = model.apply()

        set_compare_vector(tweets, result_matrix)
        dump(tweets, tweets_applied_filename, tweets_applied_dirname)

        log_and_print(logging.INFO, 'tweets applied and stored at {PATH}'.format(PATH=tweets_applied_filepath))

    elif 'tfidf' in args.subparser:
        log_and_print(logging.INFO, 'apply tfidf to dataset')
        dataset_filepath = args.dataset
        dataset_dirname, dataset_filename = split_filepath(dataset_filepath)
        dataset_applied_filepath = args.dataset_applied
        dataset_applied_dirname, dataset_applied_filename = split_filepath(dataset_applied_filepath)

        dataset = load(dataset_filename, dataset_dirname)

        news_num = dataset.news.length()
        documents = dataset.get_documents()

        set_compare_vector(documents, dataset.tf_idf_matrix)
        news, tweets = documents[:news_num], documents[news_num:]
        dump((news, tweets), dataset_applied_filename, dataset_applied_dirname)

        log_and_print(logging.INFO, 'dataset applied and stored at {PATH}'.format(
            PATH=dataset_applied_filepath))

        if args.subparser == 'tfidf_dataset':
            pass
        elif args.subparser == 'tfidf_tweets':
            log_and_print(logging.INFO, 'apply tfidf to tweets')
            tweets_filepath = args.tweets
            tweets_dirname, tweets_filename = split_filepath(tweets_filepath)
            tweets_applied_filepath = args.tweets_applied
            tweets_applied_dirname, tweets_applied_filename = split_filepath(tweets_applied_filepath)

            tweets = load(tweets_filename, tweets_dirname)

            texts = map(lambda x: x.get_text(), tweets)
            texts = lemmatize_texts(texts)
            _, result_matrix = build_tf_idf_matrix(texts, vocabulary=dataset.corpus)
            set_compare_vector(tweets, result_matrix)

            dump(tweets, tweets_applied_filename, tweets_applied_dirname)
            log_and_print(logging.INFO, 'tweets applied and stored at {PATH}'.format(
                PATH=tweets_applied_filepath))
        else:
            raise Exception('unexpected tfidf parser')

    elif args.subparser == 'build_recommendation':
        input_dir = args.input_dir
        output_dir = args.output_dir
        tweets_applied_filename = args.tweets_applied
        dataset_applied_filename = args.dataset_applied

        news, tweets = load(dataset_applied_filename, input_dir)
        is_dataset = True
        if tweets_applied_filename:
            tweets = load(tweets_applied_filename, input_dir)
            is_dataset = False

        recommendation, correct_news_idxs = recommend(news, tweets, top_size=10, is_dataset=is_dataset)
        dump((recommendation, correct_news_idxs), 'recommendation', output_dir)

        log_and_print(logging.INFO, 'recommendation builded and stored at {PATH}'.format(PATH=os.path.join(output_dir, 'recommendation')))

    elif 'recommend' in args.subparser:
        dataset_applied_filepath = args.dataset_applied
        dataset_applied_dirname, dataset_applied_filename = split_filepath(dataset_applied_filepath)

        dump_filepath = args.dump

        news, tweets = load(dataset_applied_filename, dataset_applied_dirname)

        if args.subparser == 'recommend_dataset':
            log_and_print(logging.INFO, 'build recommendation')
            recommendation, correct_news_idxs = recommend(news, tweets, top_size=10, evaluate=True)
            log_and_print(logging.INFO, 'recommendation result evaluation')
            print 'RR =', RR(correct_news_idxs)
            print 'TOP1 =', TOP1(correct_news_idxs)
            print 'TOP3 =', TOP3(correct_news_idxs)

        elif args.subparser == 'recommend_tweets':
            tweets_applied_filepath = args.tweets_applied
            tweets_applied_dirname, tweets_applied_filename = split_filepath(tweets_applied_filepath)
            tweets = load(tweets_applied_filename, tweets_applied_dirname)

            recommendation, _ = recommend(news, tweets, top_size=10, evaluate=False)
        else:
            raise Exception('unexpected recommend parser')

        dump_to_csv(recommendation, dump_filepath)
        log_and_print(logging.INFO, 'recommendation dumped to {PATH}'.format(PATH=dump_filepath))







