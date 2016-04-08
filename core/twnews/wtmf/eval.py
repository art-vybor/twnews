from twnews.timeit import timeit
from multiprocessing import Pool
import random
from scipy import spatial
import math


def evaluation(Q, tweets, news, k):
    nt = []

    for i in range(len(news)):
        nt.append((news[i], Q[:,i]))

    tt = []
    for i in range(len(tweets)):
        tt.append((tweets[i], Q[:,i+len(news)]))

    top = find_topk_sim_news_to_tweets(tt,nt, k)
    random_top = get_random_top(news, tweets, k)

    atop = ATOP(top, 10)
    random_atop = ATOP(random_top, 10)
    return atop, random_atop


def get_random_top(news, tweets, k):
    set_news = set(news)
    random_top = []
    for tweet in tweets:
        sample = random.sample(set_news, k)
        random_top.append((tweet, sample))
    return random_top


def cosine_similarity(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)


def find_topk_sim_news_to_tweet(tweet_pair, news_pairs, k=10):
    tweet, tweet_latent_vector = tweet_pair
    #sim_list = [(x[0],cosine_similarity(tweet_latent_vector, x[1])[0][0]) for x in news_pairs]
    sim_list = [(x[0], cosine_similarity(tweet_latent_vector, x[1])) for x in news_pairs]

    sim_list = sorted(sim_list, key=lambda x: x[1], reverse=True)
    #print map(lambda x: x[1], sim_list[:10])
    return map(lambda x: x[0], sim_list[:k])


def f(x):
    t, news_pairs, k = x
    res = find_topk_sim_news_to_tweet(t, news_pairs, k)
    return (t[0], res)


@timeit
def find_topk_sim_news_to_tweets(tweet_pairs, news_pairs, k=10):
    p = Pool(16)
    return p.map(f, [(tweet, news_pairs, k) for tweet in tweet_pairs])


def TOPK_t(tweet, top_news, k):
    top_news = top_news[:k]
    for news in top_news:
        for url in tweet.urls:
            if url == news.link:
                return 1
    return 0


def TOPK(tweets, k):
    s = 0
    for tweet, top_news in tweets:
        s += TOPK_t(tweet, top_news, k)
    return s*1.0/len(tweets)


def ATOP(tweets, N):
    s = 0
    for k in range(1,N+1):
        s += TOPK(tweets, k)
    return s*1.0/N
