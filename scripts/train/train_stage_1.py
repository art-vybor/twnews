from sklearn.feature_extraction.text import TfidfVectorizer

from twnews.dataset.storage import NewsStorage
from twnews.utils.text_processors import Lemmatizer

news_storage = news_storage = NewsStorage()
texts = news_storage.get_texts()

#constants
wm = 1e-2

# lemmatize
lemmatizer = Lemmatizer()
lemmas_list = lemmatizer.split_texts_to_lemmas(texts)
texts = [' '.join(lemma) for lemma in lemmas_list]

# build X and corpus
tvf = TfidfVectorizer()
tfidf_matrix = tvf.fit_transform(texts)

X = tfidf_matrix.transpose()
corpus = tvf.get_feature_names()

import numpy as np
from twnews.timeit import timeit

@timeit
def build_weight_matrix(matrix):
    '''Slow and ugly realization TODO: rewrite'''
    F = X.copy().todense().tolist()
    W = []
    rows = len(F)
    columns = len(F[0])

    for i in range(rows):
        row = [1 if F[i][j] != 0.0 else wm for j in range(columns)]
        W.append(row)
    return np.array(W)


# build weight matrix
W = build_weight_matrix(X)

import pickle

W.dump('data/W')    

with open('data/X', 'wb') as f:
    pickle.dump(X, f)

with open('data/texts', 'wb') as f:
    pickle.dump(texts, f)

with open('data/words', 'wb') as f:
    pickle.dump(corpus, f)
