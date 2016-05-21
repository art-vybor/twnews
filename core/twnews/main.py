import os
import argparse
import logging
import sys
from scipy import sparse
from copy import deepcopy
import numpy as np
import heapq
from twnews import defaults
from twnews.dataset.dataset import Dataset
from twnews.resolver import resolve, url_analyse
from twnews.dataset.storage import TweetsStorage
from twnews.utils.memoize import memo_process, load, dump
from twnews.utils.text_processors import lemmatize_texts, build_tf_idf_matrix
from twnews.eval import RR, ATOP
from twnews.model.wtmf import WTMF
from twnews.model.wtmf_g import WTMF_G

#reload(logging)
logging.basicConfig(
    filename=defaults.LOG_FILE,
    level=defaults.LOG_LEVEL,
    stream=sys.stdout,
    format='%(asctime)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")


def parse_args():
    parser = argparse.ArgumentParser(description='twnews command line interface.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(dest='subparser_name', help='sub-commands')

    dataset_parser = subparsers.add_parser('dataset', help='construct dataset')
    dataset_group = dataset_parser.add_mutually_exclusive_group(required=True)
    dataset_group.add_argument('--build_automatic', dest='automatic', action='store_true', help='build automatic dataset')
    dataset_group.add_argument('--build_manual', dest='manual', action='store_true', help='build manual dataset')
    dataset_group.add_argument('--add_relations', dest='relation', action='store_true', help='add text to text relation information for builded dataset')
    dataset_parser.add_argument('--unique_words_in_tweet', dest='percent_of_unique_words', default=1.0, type=float, help='percent of unique words in tweet by corresponding news')
    dataset_parser.add_argument('--try_to_load', dest='try_to_load', action='store_true', help='try_to_load flag')

    train_parser = subparsers.add_parser('train', help='train model')
    train_group = train_parser.add_mutually_exclusive_group(required=True)
    train_group.add_argument('--wtmf', dest='wtmf', action='store_true', help='train wtmf model')
    train_group.add_argument('--wtmf_g', dest='wtmf_g', action='store_true', help='train wtmf-g model')
    train_group.add_argument('--tfidf', dest='tfidf', action='store_true', help='train tfidf model')
    train_parser.add_argument('--try_to_load', dest='try_to_load', action='store_true', help='try_to_load flag')

    apply_parser = subparsers.add_parser('apply', help='apply model')
    apply_group = apply_parser.add_mutually_exclusive_group(required=True)
    apply_group.add_argument('--wtmf', dest='wtmf', action='store_true', help='apply wtmf model')
    apply_group.add_argument('--wtmf_g', dest='wtmf_g', action='store_true', help='apply wtmf-g model')
    apply_group.add_argument('--tfidf', dest='tfidf', action='store_true', help='apply tfidf model')

    pipe_parser = subparsers.add_parser('pipe', help='run pipe commands')
    pipe_group = pipe_parser.add_mutually_exclusive_group(required=True)
    pipe_group.add_argument('--run_pipe', dest='run_pipe', action='store_true', help='start total pipeline of model build and eval')
    pipe_group.add_argument('--resolve', dest='resolve', action='store_true', help='resolve urls from tweets')
    pipe_group.add_argument('--eval', dest='eval', action='store_true', help='eval')
    pipe_group.add_argument('--recommend', dest='recommend', action='store_true', help='recommend')
    pipe_group.add_argument('--analyse_urls', dest='analyze_urls', action='store_true', help='analyze resolved urls')
    pipe_group.add_argument('--dump_to_csv', dest='dump_to_csv', action='store_true', help='dump_to_csv')
    pipe_parser.add_argument('--try_to_load', dest='try_to_load', action='store_true', help='try_to_load flag')



    args = parser.parse_args()

    return args


def main():
    logging.info('--------------- Twnews started ------------------')
    args = parse_args()

    if args.subparser_name == 'dataset':
        #logging.info('--------------- automatic dataset ------------------')
        if args.automatic:
            dataset = memo_process(lambda: Dataset(fraction=1, percent_of_unique_words=args.percent_of_unique_words), 'dataset', try_to_load=args.try_to_load)
            lemmatized_texts = memo_process(lambda: lemmatize_texts(dataset.get_texts()), 'lemmatized_texts',try_to_load=args.try_to_load)
            corpus, tf_idf_matrix = memo_process(lambda: build_tf_idf_matrix(lemmatized_texts), 'tf_idf_corpus', try_to_load=args.try_to_load)
        elif args.manual:
            manual_tweets = load('manual_tweets')
            dataset = memo_process(lambda: Dataset(fraction=1, init_by_prepared_tweets=manual_tweets, percent_of_unique_words=args.percent_of_unique_words), 'dataset', try_to_load=args.try_to_load)
            lemmatized_texts = memo_process(lambda: lemmatize_texts(dataset.get_texts()), 'lemmatized_texts', try_to_load=args.try_to_load)
            corpus, tf_idf_matrix = memo_process(lambda: build_tf_idf_matrix(lemmatized_texts), 'tf_idf_corpus', try_to_load=args.try_to_load)
        elif args.relation:
            dataset = load('dataset')
            dataset.init_text_to_text_links()
            dump(dataset, 'dataset')

    elif args.subparser_name == 'train':
        dataset = load('dataset')
        corpus, tf_idf_matrix = load('tf_idf_corpus')
        lemmatized_texts = load('lemmatized_texts')

        news_num = dataset.news.length()
        documents = dataset.get_dataset_texts()
        print len(lemmatized_texts), len(corpus)

        compare_vector_matrix = None
        if args.wtmf:
            model = WTMF(lemmatized_texts, corpus, tf_idf_matrix, try_to_load=args.try_to_load)
            model.build()
            compare_vector_matrix = model.Q
        elif args.wtmf_g:
            links = dataset.text_to_text_links
            model = WTMF_G(lemmatized_texts, corpus, tf_idf_matrix, links, try_to_load=args.try_to_load)
            model.build()
            compare_vector_matrix = model.Q
        elif args.tfidf:
            compare_vector_matrix = tf_idf_matrix


        set_wtmf_compare_vector(documents, compare_vector_matrix)
        news, tweets = documents[:news_num], documents[news_num:]
        dump(news, 'news_applied')
        dump(tweets, 'tweets_applied')

    elif args.subparser_name == 'apply':
        corpus, tf_idf_matrix = load('tf_idf_corpus')
        dataset = load('dataset')
        tweets = dataset.tweets.get_dataset_texts()[:1000]
        #tweets = TweetsStorage(defaults.TWEETS_PATH, 0.01)
        #documents = tweets.get_dataset_texts()[:1000]

        texts = map(lambda x: x.get_text(), tweets)
        texts = lemmatize_texts(texts)
        _, tf_idf_matrix = build_tf_idf_matrix(texts, vocabulary=corpus)

        result_matrix = None
        if args.wtmf:
            model = WTMF(texts, corpus, tf_idf_matrix, try_to_load=True)
            result_matrix = model.apply()
        elif args.wtmf_g:
            raise Exception('not realized yet')
            #links = dataset.text_to_text_links
            #model = WTMF_G(texts, corpus, tf_idf_matrix, links, try_to_load=True)
            #result_matrix = model.apply()
        elif args.tfidf:
            _, result_matrix = build_tf_idf_matrix(texts, vocabulary=corpus)

        set_wtmf_compare_vector(tweets, result_matrix)
        dump(tweets, 'tweets_applied')

    elif args.subparser_name == 'pipe':
        if args.resolve:
            resolve(sample_size=None)

        elif args.analyze_urls:
            url_analyse()

        elif args.recommend:
            news = load('news_applied')
            tweets = load('tweets_applied')

            recommendation = recommend(news, tweets, top_size=10)
            dump(recommendation, 'recommendation')

        elif args.eval:
            recommendation = load('recommendation')
            print 'RR =',RR(recommendation)

        elif args.dump_to_csv:
            recommendation = load('recommendation')
            filepath = os.path.join(defaults.TMP_FILE_DIRECTORY, 'recommendation.csv')
            dump_to_csv(recommendation, filepath)

def dump_to_csv(recommendation, filename):
    batch_size = 1000

    batchs = [recommendation[i:i + batch_size] for i in xrange(0, len(recommendation), batch_size)]
    for batch_idx, recoms_batch in enumerate(batchs):
        with open(filename, 'w') as f:
            for i, (tweet, news_list) in enumerate(recoms_batch):
                f.write('%d) %s\n' % (i, tweet.text.replace('\n', ' ').encode('utf-8')))
                f.write('%s\n' % tweet.tweet_id)
                if tweet.urls:
                    f.write('%s\n' % ' '.join(tweet.urls))
                for news, score in news_list:
                    f.write('\t%s\n' % news)
                    f.write('\t%s\n' % news.link)
                    f.write('\t---------------------\n')


def set_wtmf_compare_vector(documents, Q):
    logging.info('Start setting of compare vector for {NUM} documents'.format(NUM=len(documents)))
    for i in range(Q.shape[1]):
        compare_vector = Q[:, i]#.toarray().tolist()
        #compare_vector = map(lambda x: x[0], compare_vector)
        documents[i].set_compare_vector(compare_vector)
        if i % 1000 == 0:
            print '%.2f%% finished' % (i*100.0/Q.shape[1])


def recommend(news, tweets, top_size=10):
    from sklearn.metrics.pairwise import cosine_similarity

    # def convert_to_compare_matrix(documents):
    #     dim = documents[0].compare_vector.shape[0]
    #
    #     compare_matrix = sparse.csr_matrix((dim, len(documents)))
    #
    #     for i, document in enumerate(documents):
    #         compare_matrix[:, i] = document.compare_vector
    #     return compare_matrix

    def convert_to_compare_matrix(documents):
        dim = documents[0].compare_vector.shape[0]

        data, row_idxs, column_idxs = [], [], []
        for column_idx, document in enumerate(documents):
            rows, _, values = sparse.find(document.compare_vector)
            for i, value in enumerate(values):
                data.append(values[i])
                row_idxs.append(rows[i])
                column_idxs.append(column_idx)

        compare_matrix = sparse.csr_matrix((data, (row_idxs, column_idxs)), shape=(dim, len(documents)))
        return compare_matrix

    tweets_matrix = convert_to_compare_matrix(tweets)
    print 'tweets converted'
    news_matrix = convert_to_compare_matrix(news)
    print 'news converted'


    mat = cosine_similarity(tweets_matrix.T, news_matrix.T)
    print 'matrix builded'

    recommendation = []
    for tweet_idx, tweet in enumerate(tweets):
        news_list = [(single_news, mat[tweet_idx][news_idx]) for news_idx, single_news in enumerate(news)]
        news_list_top = heapq.nlargest(top_size, news_list, key=lambda x: x[1])

        recommendation.append((tweet, news_list_top))

    return recommendation