import argparse
import logging
import sys
from scipy import sparse
import numpy as np
import heapq
from twnews import defaults
from twnews.dataset.dataset import Dataset
from twnews.resolver import resolve, url_analyse
from twnews.utils.memoize import memo_process, load, dump
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
    pipe_group.add_argument('--eval', dest='eval', action='store_true', help='eval')
    pipe_group.add_argument('--apply_wtmf', dest='apply_wtmf', action='store_true', help='apply wtmf')
    pipe_group.add_argument('--recommend', dest='recommend', action='store_true', help='recommend')
    pipe_group.add_argument('--analyse_urls', dest='analyze_urls', action='store_true', help='analyze resolved urls')
    pipe_group.add_argument('--apply_tfidf', dest='apply_tfidf', action='store_true', help='apply tfidf')

    pipe_group.add_argument('--dump_to_csv', dest='dump_to_csv', action='store_true', help='dump_to_csv')

    parser.add_argument('--try_to_load', dest='try_to_load', action='store_true', help='try_to_load flag')

    args = parser.parse_args()

    return args


def main():
    logging.info('--------------- Twnews started ------------------')
    args = parse_args()

    if args.train_wtmf:
        dataset = load('dataset')
        corpus, tf_idf_matrix = load('tf_idf_corpus')
        lemmatized_texts = load('lemmatized_texts')
        news_num = dataset.news.length()
        documents = dataset.get_dataset_texts()

        print len(lemmatized_texts), len(corpus)
        train_wtmf(documents, corpus, tf_idf_matrix, lemmatized_texts, args)

        news, tweets = documents[:news_num], documents[news_num:]
        dump(news, 'news_applied')
        dump(tweets, 'tweets_applied')

    elif args.apply_wtmf:
        corpus, _ = load('tf_idf_corpus')
        dataset = load('dataset')
        documents = dataset.tweets.get_dataset_texts()#[:100]

        from twnews.dataset.storage import TweetsStorage
        tweets = TweetsStorage(defaults.TWEETS_PATH, 0.01)
        documents = tweets.get_dataset_texts()[:1000]

        apply_wtmf(documents, corpus)

        dump(documents, 'documents_applied')

    elif args.resolve:
        resolve(sample_size=None)
    elif args.analyze_urls:
        url_analyse()
    elif args.dataset:
        dataset = memo_process(lambda: Dataset(fraction=1), 'dataset', try_to_load=args.try_to_load)
        lemmatized_texts = memo_process(lambda: lemmatize_texts(dataset.get_texts()), 'lemmatized_texts',try_to_load=args.try_to_load)
        corpus, tf_idf_matrix = memo_process(lambda: build_tf_idf_matrix(lemmatized_texts), 'tf_idf_corpus', try_to_load=args.try_to_load)

    elif args.recommend:
        news = load('news_applied')
        tweets = load('documents_applied')

        recommendation = recommend(news, tweets, top_size=10)

        dump(recommendation, 'recommendation')
    elif args.apply_tfidf:
        #print 1
        corpus, tf_idf_matrix = load('tf_idf_corpus')
        dataset = load('dataset')
        news_num = dataset.news.length()

        # documents = dataset.get_dataset_texts()
        # set_wtmf_compare_vector(documents, tf_idf_matrix)
        # news, tweets = documents[:news_num], documents[news_num:]
        # dump(news, 'news_applied')
        # dump(tweets, 'tweets_applied')

        #documents = dataset.tweets.get_dataset_texts()#[:100]

        from twnews.dataset.storage import TweetsStorage
        #tweets = TweetsStorage(defaults.TWEETS_PATH, 0.01)
        #documents = tweets.get_dataset_texts()[:1000]
        documents = load('good_tweets')
        documents = documents[:50000]
        
        apply_tfidf(documents, corpus)
        dump(documents, 'documents_applied')
    elif args.eval:
        recommendation = load('recommendation')
        print 'RR =',RR(recommendation)
    elif args.dump_to_csv:
        recommendation = load('recommendation')




def RR(recoms):
    RR = 0.0
    for tweet, news in recoms:
        for i, single_news_tuple in enumerate(news):
            single_news, score = single_news_tuple
            if single_news.link in tweet.urls:
                RR += 1.0 / (i + 1)
                break
    return RR / len(recoms)


def train_wtmf(documents, corpus, tf_idf_matrix, lemmatized_texts, args):
    model = WTMF(lemmatized_texts, corpus, tf_idf_matrix, try_to_load=args.try_to_load)
    model.build()
    set_wtmf_compare_vector(documents, model.Q)


def apply_wtmf(documents, corpus):
    texts = map(lambda x: x.get_text(), documents)
    texts = lemmatize_texts(texts)
    _, tf_idf_matrix = build_tf_idf_matrix(texts, vocabulary=corpus)

    model = WTMF(texts, corpus, tf_idf_matrix, try_to_load=True)
    Q = model.apply()
    set_wtmf_compare_vector(documents, Q)


def apply_tfidf(documents, corpus):
    texts = map(lambda x: x.get_text(), documents)
    texts = lemmatize_texts(texts)
    _, tf_idf_matrix = build_tf_idf_matrix(texts, vocabulary=corpus)
    set_wtmf_compare_vector(documents, tf_idf_matrix)


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