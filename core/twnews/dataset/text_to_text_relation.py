import heapq
from collections import defaultdict
from datetime import timedelta
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity

from twnews.utils.memoize import load
from twnews.utils.text_processors import Lemmatizer, extract_entities
from twnews.utils.extra import timeit


def get_text_to_text_relation(news, tweets, k=3):
    """result is a list of index pairs in array news+tweets"""
    # tweets = tweets[:500]
    # news = news[:500]

    tweet_to_tweet_hashtags = get_tweet_to_tweet_hashtags_relation(tweets, k)
    NE_set = get_NE_from_news(news)
    tweet_to_tweet_NER = get_tweet_to_tweet_NER_relation(tweets, NE_set, k)
    tweet_to_tweet_time = get_document_to_documet_time_relation(tweets, k)
    news_to_news_time = get_document_to_documet_time_relation(news, k)

    total_relations = tweet_to_tweet_hashtags #| tweet_to_tweet_NER | tweet_to_tweet_time | news_to_news_time

    return filter(lambda x: x[0] != x[1], total_relations)


@timeit
def get_tweet_to_tweet_hashtags_relation(tweets, k):
    def num_of_common_hashtags(tweet1, tweet2):
        hashtags1 = set(tweet1.hastags.keys())
        hashtags2 = set(tweet2.hastags.keys())
        return len(hashtags1 & hashtags2)

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
    print 'hashtags:', len(hashtags)

    hashtag_to_tweets = defaultdict(list)
    for tweet in tweets:
        for word in tweet.words:
            if word in hashtags:
                tweet.hastags[word] = None
                hashtag_to_tweets[word].append(tweet)

    result = set()
    for tweet in tweets:
        for hashtag in tweet.hastags.keys():
            linked_tweets = hashtag_to_tweets[hashtag]
            linked_tweets = filter(lambda x: num_of_common_hashtags(x, tweet) >=2, linked_tweets)

            top_k = get_top_k_by_time(tweet, linked_tweets, k)
            if top_k:
                for elem in top_k:
                    result.add((tweet.index, elem.index))
    print 'tweet_to_tweet_hashtags', len(result)
    return result


@timeit
def get_tweet_to_tweet_NER_relation(tweets, NE_set, k):
    NE_to_tweets = defaultdict(list)

    for tweet in tweets:
        tweet.named_entities = []
        for word in tweet.words:
            if word in NE_set:
                tweet.named_entities.append(word)
                NE_to_tweets[word].append(tweet)

    result = set()
    for tweet in tweets:
        for entity in tweet.named_entities:
            linked_tweets = NE_to_tweets[entity]
            top_k = get_top_k_by_time(tweet, linked_tweets, k)
            if top_k:
                for elem in top_k:
                    result.add((tweet.index, elem.index))
    print 'tweet_to_tweet_NER', len(result)
    return result


@timeit
def get_document_to_documet_time_relation(documents, k):
    similarity = get_similarity_matrix(documents, documents)

    result = set()
    for d1_index, d1 in enumerate(documents):
        related_documents = []
        for d2_index, d2 in enumerate(documents):
            if document_date_distanse(d1,d2) < timedelta(hours=24):
                related_documents.append((d2, similarity[d1_index][d2_index]))

        top_k = heapq.nlargest(k, related_documents, key=lambda x: x[1])
        if top_k:
            for elem, sim in top_k:
                result.add((d1.index, elem.index))
    print 'document_to_documet_time_relation', len(result)
    return result


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
    print 'NE:', len(result), 'errors:', errors
    return result


def get_similarity_matrix(documents_1, documents_2):
    corpus, tf_idf_matrix = load('tf_idf_corpus')

    def convert_to_compare_matrix(documents):
        dim = len(corpus)

        data, row_idxs, column_idxs = [], [], []
        for column_idx, document in enumerate(documents):
            rows, _, values = sparse.find(tf_idf_matrix[:,document.index])
            for i, value in enumerate(values):
                data.append(values[i])
                row_idxs.append(rows[i])
                column_idxs.append(column_idx)

        compare_matrix = sparse.csr_matrix((data, (row_idxs, column_idxs)), shape=(dim, len(documents)))
        return compare_matrix

    matrix_1 = convert_to_compare_matrix(documents_1)
    print 'matrix 1 builded'

    matrix_2 = convert_to_compare_matrix(documents_2)
    print 'matrix 2 builded'

    mat = cosine_similarity(matrix_1.T, matrix_2.T)
    print 'similarity matrix builded'
    return mat


def document_date_distanse(d1, d2):
    return max(d1.date, d2.date) - min(d1.date, d2.date)



from datetime import timedelta

def get_top_k_by_time(base_document, documents, k):
    documents = filter(lambda x: x.index != base_document.index, documents)
    documents = filter(lambda x: document_date_distanse(x, base_document) < timedelta(hours=12), documents)
    documents = sorted(documents, key=lambda x: document_date_distanse(x, base_document))
    return documents[:k]
