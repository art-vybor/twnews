import heapq
import logging

from twnews.utils.extra import timeit
from twnews.utils.text_processors import Lemmatizer, extract_entities


def get_text_to_text_relation(news, tweets, similarity_matrix, k=10):
    """result is a list of index pairs in array news+tweets"""
    # tweets = tweets[:500]
    # news = news[:500]

    tweet_to_tweet_hashtags = get_tweet_to_tweet_hashtags_relation(tweets, k, similarity_matrix)
    logging.info('num of tweet to tweet by hashtags relation %s' % len(tweet_to_tweet_hashtags))

    NE_set = get_NE_from_news(news)
    tweet_to_tweet_NER = get_tweet_to_tweet_NER_relation(tweets, NE_set, k, similarity_matrix)
    logging.info('num of tweet to tweet by NER relation %s' % len(tweet_to_tweet_NER))

    tweet_to_tweet_time = get_document_to_documet_time_relation(tweets, k, similarity_matrix)
    logging.info('num of tweet to tweet by time relation %s' % len(tweet_to_tweet_time))

    news_to_news_time = get_document_to_documet_time_relation(news, k, similarity_matrix)
    logging.info('num of news to news by time relation %s' % len(news_to_news_time))

    total_relations = filter_links(tweet_to_tweet_hashtags | tweet_to_tweet_NER | tweet_to_tweet_time | news_to_news_time)
    logging.info('num of total relations %s' % len(total_relations))
    return filter_links(total_relations)


def filter_links(links):
    result = set()
    for i,j in list(links):
        result.add((min(i,j), max(i,j)))
    return result

@timeit
def get_tweet_to_tweet_hashtags_relation(tweets, k, similarity_matrix):
    def get_all_hashtags(tweets):
        lemmatizer = Lemmatizer()
        hashtags = {}
        for tweet in tweets:
            tweet_hashtags = map(lemmatizer.lemmatize, tweet.hastags.keys())
            for hashtag in tweet_hashtags:
                hashtags[hashtag] = hashtags[hashtag] + 1 if hashtag in hashtags else 1

        for h, v in hashtags.items():#sorted(hashtags.items(), key=lambda x: x[1]):
            if v > 10:
                del hashtags[h]

        return set(hashtags.keys())

    hashtags = get_all_hashtags(tweets)
    #print 'hashtags:', len(hashtags)

    for tweet in tweets:
        tweet.named_entities = set()
        for word in tweet.words:
            if word in hashtags:
                tweet.hastags[word] = None

    result = set()
    for t1 in tweets:
        candidates = []
        for t2 in tweets:
            if t1.index != t2.index and \
               similarity_matrix[t1.index][t2.index] < 0.99 and \
                len(set(t1.hastags.keys()) & set(t2.hastags.keys())) >= 2:
                    candidates.append(t2)

        top_k = get_top_k_by_time(t1, candidates, k)
        if top_k:
            for elem in top_k:
                result.add((t1.index, elem.index))

    #print 'tweet_to_tweet_hashtags', len(result)
    return filter_links(result)


@timeit
def get_tweet_to_tweet_NER_relation(tweets, NE_set, k, similarity_matrix):
    for tweet in tweets:
        tweet.named_entities = set()
        for word in tweet.words:
            if word in NE_set:
                tweet.named_entities.add(word)

    result = set()
    for t1 in tweets:
        candidates = []
        for t2 in tweets:
            if t1.index != t2.index and \
               similarity_matrix[t1.index][t2.index] < 0.99 and \
                len(t1.named_entities & t2.named_entities) >= 2:
                    candidates.append(t2)

        top_k = get_top_k_by_time(t1, candidates, k)
        if top_k:
            for elem in top_k:
                result.add((t1.index, elem.index))

    #print 'tweet_to_tweet_NER', len(result)
    return filter_links(result)


@timeit
def get_document_to_documet_time_relation(documents, k, similarity_matrix):

    result = set()
    for d1 in documents:
        related_documents = []
        for d2 in documents:
            similarity = similarity_matrix[d1.index][d2.index]
            if (0.3 < similarity and similarity < 0.99) and \
               d1.index != d2.index and \
               document_date_distanse(d1, d2) < timedelta(hours=24):
                related_documents.append((d2, similarity))

        top_k = heapq.nlargest(k, related_documents, key=lambda x: x[1])
        if top_k:
            for elem, sim in top_k:
                result.add((d1.index, elem.index))
    #print 'document_to_documet_time_relation', len(result)
    return filter_links(result)


def get_NE_from_news(news_documents):
    lemmatizer = Lemmatizer()
    result = set()
    errors = 0
    for i, news in enumerate(news_documents):
        try:
            ents = extract_entities(lemmatizer, news.summary)
        except Exception as e:
            errors += 1
            ents = set()
        result.update(ents)
    #print 'NE:', len(result), 'errors:', errors
    return result


def document_date_distanse(d1, d2):
    return max(d1.date, d2.date) - min(d1.date, d2.date)



from datetime import timedelta

def get_top_k_by_time(base_document, documents, k):
    documents = filter(lambda x: x.index != base_document.index, documents)
    documents = filter(lambda x: document_date_distanse(x, base_document) < timedelta(hours=12), documents)
    documents = sorted(documents, key=lambda x: document_date_distanse(x, base_document))
    return documents[:k]
