import argparse
from twnews.dataset.storage import NewsStorage
from twnews.dataset.dataset import Dataset
from twnews.wtmf.wtmf import WTMF
from twnews.wtmf.eval import evaluation

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
        news = dataset.news_storage.get_news()
        tweets = dataset.dataset
        tweets_texts = [tweet.text for tweet in tweets]

        for iteration in [1,2,3,4,5,6,7,8,9,10]:
            for dim in [10,20,30,40,50,60,70,80,90,100]:
                model = WTMF(news_texts+tweets_texts)
                model.iterations_num=iteration
                model.dim=dim
                model.build(try_to_load=False)
                #print model
                atop, ratop = evaluation(model.Q, tweets, news, k=10)

                with open('benchmark', 'w+') as f:
                    f.write(str(model) + '\n')
                    f.write('\tatop: %s\n' % atop)
                    f.write('\tratop: %s\n' % ratop)



