# def RR(recoms):
#     RR = 0.0
#     for tweet, news in recoms:
#         for i, single_news_tuple in enumerate(news):
#             single_news, score = single_news_tuple
#             if single_news.link in tweet.urls:
#                 RR += 1.0 / (i + 1)
#                 break
#     return RR / len(recoms)
#
#
# def ATOPu(tweet, news):
#     N = len(news)
#     k = N
#
#     for idx, (news, score) in enumerate(news):
#         for url in tweet.urls:
#             if url == news.link:
#                 k = idx+1
#     #print 'N', N, 'k', k
#     return (N - k) * 1.0 / (N - 1)
#
# def ATOP(recoms):
#     ATOPu_sum = 0
#     for tweet, news in recoms:
#         a = ATOPu(tweet, news)
#         ATOPu_sum += a
# #        print 'ATOPu', a
#     return ATOPu_sum / len(recoms)


def RR(correct_news_idxs):
    RR = 0.0
    for idx in correct_news_idxs:
        RR += 1.0 / idx
    return RR / len(correct_news_idxs)


def ATOPu(k, N):
    return (N - k) * 1.0 / (N - 1)


def ATOP(correct_news_idxs, total_news):
    ATOPu_sum = 0
    for idx in correct_news_idxs:
        #print idx, total_news
        a = ATOPu(idx, total_news)
        #print a
        ATOPu_sum += a
#        print 'ATOPu', a
    return ATOPu_sum *1.0 / len(correct_news_idxs)


def TOPI(correct_news_idxs, I):
    TOPI_sum = 0.0
    for idx in correct_news_idxs:
        if idx <= I:
            TOPI_sum += 1
    return TOPI_sum * 1.0 / len(correct_news_idxs)


def TOP1(correct_news_idxs):
    return TOPI(correct_news_idxs, 1)


def TOP3(correct_news_idxs):
    return TOPI(correct_news_idxs, 3)
