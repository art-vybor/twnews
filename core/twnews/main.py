import argparse
from twnews.resolver import resolve, url_analyse
from twnews.dataset.dataset import Dataset
from twnews.wtmf.wtmf import WTMF


def parse_args():
    parser = argparse.ArgumentParser(description='twnews command line interface.')
    
    parser.add_argument('--run_pipe', dest='run_pipe', action='store_true', help='start total pipeline of model build and eval')
    parser.add_argument('--resolve', dest='resolve', action='store_true', help='resolve urls from tweets')
    parser.add_argument('--analyse_urls', dest='analyze_urls', action='store_true', help='analyze resolved urls')

    args = parser.parse_args()

    args_value = [args.run_pipe, args.resolve, args.analyze_urls]
    if sum(map(int, args_value)) > 1:
        print 'There are too many input arguments'
        import sys
        sys.exit(0)

    return args


def main():
    args = parse_args()
    
    if args.run_pipe:
        dataset = Dataset(fraction=1, use_dataset_if_exist=True)
        news_texts = dataset.news_storage.get_texts()
        news = dataset.news_storage.get_news()
        tweets = dataset.dataset
        tweets_texts = [tweet.text for tweet in tweets]


        model = WTMF(tweets, news, news_texts+tweets_texts)
        model.init_model(try_to_load=True)

        #for iteration in [1,2,3,4,5,6,7,8,9,10]:
        for dim in [50,60,70,80,90,100]:
            #model.iterations_num=iteration
            model.dim=dim
            model.build(try_to_load=False)

    elif args.resolve:
        resolve()
    elif args.analyze_urls:
        url_analyse()



