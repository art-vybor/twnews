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

logging.basicConfig(
    filename=defaults.LOG_FILE,
    level=defaults.LOG_LEVEL,
    stream=sys.stdout,
    format='%(asctime)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")



def wtmg_test((options, dataset)):
    model = WTMF_G(dataset, options=options)
    model.build()

def main():
    args = parse_args()
    import sys
    sys.exit(0)
    logging.info('--------------- Twnews started ------------------')

    if args.subparser_name == 'dataset':
        log_and_print(logging.INFO, 'dataset builder')

        if args.automatic or args.manual:
            dataset = None
            if args.automatic:
                log_and_print(logging.INFO, 'building automatic dataset')
                dataset = Dataset(fraction=1, percent_of_unique_words=args.percent_of_unique_words)
            elif args.manual:
                log_and_print(logging.INFO, 'building manual dataset')
                manual_tweets = load('manual_tweets')
                dataset = Dataset(fraction=1, init_by_prepared_tweets=manual_tweets, percent_of_unique_words=args.percent_of_unique_words)

            dataset.init_text_to_text_links()

            dump(dataset, dataset.name())
            dump(dataset, 'dataset')

    elif args.subparser_name == 'train':
        log_and_print(logging.INFO, 'train model')

        if args.dataset_file:
            dirname, filename = os.path.dirname(args.dataset_file), os.path.basename(args.dataset_file)
            dataset = load(filename, dirname)
        else:
            dataset = load('dataset')

        if args.wtmf:
            log_and_print(logging.INFO, 'train wtmf')

            model = WTMF(dataset)
            model.build()

        elif args.wtmf_g:
            log_and_print(logging.INFO, 'train wtmf-g')
            options_list = []
            from multiprocessing import Pool
            #
            # for delta in [0.06, 0.08, 0.1, 0.12, 0.14]:
            #     for lmbd in [6, 8, 10, 12, 14]:
            #for wm in [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.5]:
            #for dim in [160, 170, 180, 190, 200, 210, 220, 230]:
            options = {
                'DIM': 220,
                'WM': 5,
                'ITERATIONS': 1,
                'DELTA': 0.06,
                'LAMBDA': 6
            }
            from copy import deepcopy
            options = deepcopy(options)
            options_list.append((options, dataset))

            wtmg_test((options, dataset))
            # pool = Pool(8)
            # pool.map(wtmg_test, options_list)

            #wtmg_test(options)
                    # model = WTMF_G(dataset, options=options)
                    # model.build()

        elif args.tfidf:
            log_and_print(logging.INFO, 'apply tfidf model to dataset')
            news_num = dataset.news.length()
            documents = dataset.get_documents()

            set_compare_vector(documents, dataset.tf_idf_matrix)
            news, tweets = documents[:news_num], documents[news_num:]
            dump((news, tweets), 'dataset_applied')
            #dump(tweets, 'dataset_tweets_applied')
    #
    # elif args.subparser_name == 'apply':
    #     log_and_print(logging.INFO, 'apply model')
    #     corpus, tf_idf_matrix = load('tf_idf_corpus')
    #     dataset = load('dataset')
    #     tweets = dataset.tweets.get_documents()[:1000]
    #     #tweets = TweetsStorage(defaults.TWEETS_PATH, 0.01)
    #     #documents = tweets.get_dataset_texts()[:1000]
    #
    #     texts = map(lambda x: x.get_text(), tweets)
    #     texts = lemmatize_texts(texts)
    #     _, tf_idf_matrix = build_tf_idf_matrix(texts, vocabulary=corpus)
    #
    #     result_matrix = None
    #     if args.wtmf:
    #         log_and_print(logging.INFO, 'apply wtmf')
    #         model = WTMF(texts, corpus, tf_idf_matrix, try_to_load=True)
    #         result_matrix = model.apply()
    #     elif args.wtmf_g:
    #         log_and_print(logging.INFO, 'apply wtmg-g')
    #         raise Exception('not realized yet')
    #         #links = dataset.text_to_text_links
    #         #model = WTMF_G(texts, corpus, tf_idf_matrix, links, try_to_load=True)
    #         #result_matrix = model.apply()
    #     elif args.tfidf:
    #         log_and_print(logging.INFO, 'apply tf_idf')
    #         _, result_matrix = build_tf_idf_matrix(texts, vocabulary=corpus)
    #
    #     set_compare_vector(tweets, result_matrix)
    #     dump(tweets, 'tweets_applied')

    elif args.subparser_name == 'resolver':
        log_and_print(logging.INFO, 'url resolver')

        if args.resolve:
            log_and_print(logging.INFO, 'resolve all urls')
            resolve(sample_size=None)
        elif args.analyze:
            log_and_print(logging.INFO, 'stats of resolved urls')
            url_analyse()

    elif args.subparser_name == 'recommend':
        log_and_print(logging.INFO, 'recommendation')

        if args.recommend:
            log_and_print(logging.INFO, 'recommend tweets to news')
            news, tweets = load('dataset_applied')
            #tweets = load('dataset_tweets_applied')

            recommendation, correct_news_idxs = recommend(news, tweets, top_size=10)
            dump(recommendation, 'recommendation')
            dump((correct_news_idxs, len(news)), 'correct_news_idxs')

        elif args.recommend_by_model:
            log_and_print(logging.INFO, 'recommend dev by {MODEL}'.format(MODEL=args.recommend_by_model))
            model = load(args.recommend_by_model)
            _, _, _, _, dataset_applied = model
            news, tweets = dataset_applied

            recommendation, correct_news_idxs = recommend(news, tweets, top_size=10)
            dump(recommendation, 'recommendation')
            dump((correct_news_idxs, len(news)), 'correct_news_idxs')

        elif args.eval:
            log_and_print(logging.INFO, 'eval recommendation result')
            correct_news_idxs, total_news = load('correct_news_idxs')
            #print 'ATOP =', ATOP(correct_news_idxs, total_news)
            print 'RR =', RR(correct_news_idxs)
            print 'TOP1 =', TOP1(correct_news_idxs)
            print 'TOP3 =', TOP3(correct_news_idxs)

        elif args.dump_to_csv:
            log_and_print(logging.INFO, 'dump recommendation to csv')
            recommendation = load('recommendation')
            filepath = os.path.join(defaults.TMP_FILE_DIRECTORY, 'recommendation.csv')
            dump_to_csv(recommendation, filepath)


# random_tweets:
#     out: file_with_texts

# resolver:
#     resolve_urls

#     analyze_urls
    
# dataset
#     automatic
#         out: dataset_auto_1000_2000

# traing:
#     wtmf
#         in: dataset
#         out: model, dataset_applied
#     wtmf-g
#         in: dataset
#         out: model, dataset_applied
#     tfidf:
#         in: dataset
#         out: dataset_applied

# apply:
#     wtmf:
#         in: model, file_with_tweets 
#         out: tweets_applied
#     wtmf-g:
#         in: model, file_with_tweets 
#         out: tweets_applied
#     tfidf:
#         in: file_with_tweets, dataset
#         out: tweets_applied

# recommendation:
#     build:
#         in: dataset_applied tweets_applied
#         out: recommendation
#     eval:
#         in: recommendation
#         out: print metrics
#     dump:
#         in: recommendation
#         out: text file







