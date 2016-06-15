import heapq
import logging
from scipy import sparse
from twnews.utils.extra import progressbar_iterate


def get_index_of_correct_news(tweet, news_list):
    news_list = sorted(news_list, key=lambda x: x[1], reverse=True)
    for idx, (news, score) in enumerate(news_list):
        for url in tweet.urls:
            if url == news.link:
                return idx+1
    raise Exception('Correct news not founded')


def recommend(news, tweets, top_size=10, evaluate=False):
    from sklearn.metrics.pairwise import cosine_similarity

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

    logging.info('convert tweets to compare matrix')
    tweets_matrix = convert_to_compare_matrix(tweets)

    logging.info('convert news to compare matrix')
    news_matrix = convert_to_compare_matrix(news)

    logging.info('build cosine similarity matrix')
    mat = cosine_similarity(tweets_matrix.T, news_matrix.T)

    logging.info('build recommendation')
    recommendation = []
    correct_news_idxs = []
    for tweet_idx, tweet in enumerate(tweets):
        news_list = [(single_news, mat[tweet_idx][news_idx]) for news_idx, single_news in enumerate(news)]
        news_list_top = heapq.nlargest(top_size, news_list, key=lambda x: x[1])

        if evaluate:
            correct_news_idxs.append(get_index_of_correct_news(tweet, news_list))
        recommendation.append((tweet, news_list_top))

    return recommendation, correct_news_idxs


def set_compare_vector(documents, Q):
    logging.info('Start setting of compare vector for {NUM} documents'.format(NUM=len(documents)))
    for i in progressbar_iterate(range(Q.shape[1])):
        compare_vector = Q[:, i]#.toarray().tolist()
        #compare_vector = map(lambda x: x[0], compare_vector)
        documents[i].set_compare_vector(compare_vector)


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