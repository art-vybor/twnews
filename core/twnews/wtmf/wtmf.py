from sklearn.feature_extraction.text import TfidfVectorizer
from twnews.wtmf.text_processors import Lemmatizer
import numpy as np
from twnews.timeit import timeit
from twnews.wtmf.support_functions import memo_process, dump, load
from scipy import sparse


@timeit
def lemmatize_texts(texts):
    lemmatizer = Lemmatizer()
    lemmas_list = lemmatizer.split_texts_to_lemmas(texts)
    return [' '.join(lemma) for lemma in lemmas_list]


@timeit
def build_tf_idf_matrix(texts):
    tvf = TfidfVectorizer()
    tfidf_matrix = tvf.fit_transform(texts)

    X = tfidf_matrix.transpose()
    corpus = tvf.get_feature_names()

    return corpus, X


class WTMF:
    def __init__(self, texts):
        self.texts = texts
        self.wm = 1e-2
        self.dim = 10
        self.iterations_num = 2
        self.lmbd = 20

    def init_model(self, words_num, texts_num):
        P = np.random.rand(self.dim, words_num)
        Q = np.random.rand(self.dim, texts_num)
        P = P * 0.2 - 0.1
        Q = Q * 0.2 - 0.1
        return P, Q

    def build(self, try_to_load=False):
        lemmatized_texts = memo_process(lambda: lemmatize_texts(self.texts), 'texts', try_to_load=try_to_load)
        corpus, X = memo_process(lambda: build_tf_idf_matrix(lemmatized_texts), 'tf_idf_corpus', try_to_load=try_to_load)
        W = memo_process(lambda: self.build_weight_matrix(X), 'weights', try_to_load=try_to_load)

        texts_num = len(lemmatized_texts)
        words_num = len(corpus)

        P, Q = self.init_model(words_num, texts_num)

        X = np.array(X.todense())
        lI = np.identity(self.dim) * self.lmbd

        for i in range(self.iterations_num):
            print '%d/%d iteration' % (i+1, self.iterations_num)
            P, Q = self.iteration(P, Q, W, X, lI)

        dump(Q, 'Q')
        dump(P, 'P')
        self.P, self.Q = P, Q
        print 'finished'

    def load(self):
        self.P = load('P')
        self.Q = load('Q')

    @timeit
    def iteration(self, P, Q, W, X, lI):
        def build_row(A, w_row, x_row):
            """calc (A w_row A^T + lI)^-1 * A * w_row * x_row """
            W_i = sparse.spdiags(w_row, [0], len(w_row), len(w_row))

            AW = A.dot(W_i)
            AWA = AW.dot(A.T)
            AWAl = AWA + lI
            AWAl_inv = np.linalg.inv(AWAl)
            AWX = AW.dot(x_row.T)

            return AWAl_inv.dot(AWX)

        new_P = P.copy()
        new_Q = Q.copy()
        P = sparse.csr_matrix(P)
        Q = sparse.csr_matrix(Q)

        print 'start build P'
        for i in range(P.shape[1]):
            new_P[:, i] = build_row(Q, W[i, :], X[i, :])

            if i % 1000 == 0:
                print '%dth iteration of %d' % (i, P.shape[1])

        print 'start build Q'
        for j in range(Q.shape[1]):
            new_Q[:, j] = build_row(P, W[:, j], X[:, j])

            if j % 1000 == 0:
                print '%dth iteration of %d' % (j, Q.shape[1])

        return new_P, new_Q


    @timeit
    def build_weight_matrix(self, tf_idf_matrix):
        """Slow and ugly realization TODO: rewrite"""
        F = tf_idf_matrix.copy().todense().tolist()
        W = []
        rows = len(F)
        columns = len(F[0])

        for i in range(rows):
            row = [1 if F[i][j] != 0.0 else self.wm for j in range(columns)]
            W.append(row)
        return np.array(W)



