import argparse
from twnews.dataset.storage import NewsStorage
from twnews.dataset.dataset import Dataset
from twnews.wtmf.wtmf import WTMF


def parse_args():
    parser = argparse.ArgumentParser(description='twnews command line interface.')
    
    parser.add_argument('--run-pipe', dest='run_pipe', action='store_true', help='start total pipeline')
    # parser.add_argument('-o', metavar='filename', dest='output_file', required=False,
    #                     help='output file (default: input_file with rkt extension)')
    # parser.add_argument('--run', action='store_true', help='execute output_file')

     #group = parser.add_argument_group('debug mode')
    # group.add_argument('--stack_trace', action='store_true', help='enable stack trace printing')
    # group.add_argument('--lexems', action='store_true', help='print lexems')
    # group.add_argument('--console_tree', action='store_true', help='print ast tree to console')
    # group.add_argument('--pdf_tree', action='store_true', help='print ast tree to pdf')
    
    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    
    if args.run_pipe:
        dataset = Dataset(fraction=1, use_dataset_if_exist=True)
        news_texts = dataset.news_storage.get_texts()
        tweets_texts = [tweet.text for tweet in dataset.dataset]
        print len(dataset.dataset)
        news_model = WTMF(news_texts, prefix='news')
        news_model.build(try_to_load=True)

        tweets_model = WTMF(tweets_texts, prefix='tweets')
        tweets_model.build(try_to_load=True)

        #
        # count_true = 0
        # count_false = 0
        # for tweet in dataset.dataset:
        #
        #     news = []
        #     for url in tweet.urls:
        #         if dataset.news_storage.exists(url):
        #             news.append(dataset.news_storage.get(url))
        #     #print tweet
        #     #print news
        #     if news[0].title in tweet.text:
        #         count_true += 1
        #     else:
        #         count_false += 1
        # print count_true, count_false
        # #    print '--------'


