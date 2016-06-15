import logging
import numpy as np
from scipy import sparse
import os

from twnews.utils.memoize import load, dump
from twnews.utils.extra import timeit
from twnews.utils.logger_wrapper import log_and_print
from twnews.recommend import set_compare_vector
from twnews import defaults


class WTMF(object):
    def __init__(self, dataset=None, options=defaults.DEFAULT_WTMF_OPTIONS, model_name=False, dirname=defaults.TMP_FILE_DIRECTORY):
        P, Q = None, None
        dataset_applied = None
        self.dirname = dirname

        if model_name:
            logging.info('model will be loaded, all arguments will be ignored')
            dataset, options, P, Q, dataset_applied = self.load_model(model_name)

        self.dataset = dataset
        self.texts = dataset.lemmatized_texts
        self.words = dataset.corpus
        self.X = dataset.tf_idf_matrix
        self.P, self.Q = P, Q
        self.dataset_applied = dataset_applied
        self.options = options


        logging.info('model {NAME} of {TEXTS_NUM} texts and {WORDS_NUM} words initialized'.
                      format(NAME=self.name(), TEXTS_NUM=len(self.texts), WORDS_NUM=len(self.words)))

    def load_model(self, name=None):
        if not name:
            name = self.name()
        return load(name, self.dirname)

    def save_model(self, iterations=None):
        self.apply_to_dataset()

        if iterations:
            iterations_backup = self.options['ITERATIONS']
            self.options['ITERATIONS'] = iterations

        dump((self.dataset, self.options, self.P, self.Q, self.dataset_applied), self.name(), self.dirname)

        log_and_print(logging.INFO, 'model dumped to {PATH}'.format(PATH=os.path.join(self.dirname, self.name())))

        if iterations:
            self.options['ITERATIONS'] = iterations_backup

    def name(self):
        return '{TYPE}_({DATASET})_{DIM}_{ITERATIONS}_{LAMBDA}_{WM}'.format(
            TYPE=self.__class__.__name__,
            DATASET=self.dataset.name(),
            **self.options
        )

    def __str__(self):
        return self.name()

    def init_PQ(self):
        P = np.random.rand(self.options['DIM'], len(self.words))
        P = P * 0.2 - 0.1
        P = sparse.csr_matrix(P)

        Q = np.random.rand(self.options['DIM'], len(self.texts))
        Q = Q * 0.2 - 0.1
        Q = sparse.csr_matrix(Q)

        return P, Q

    def build(self):
        if self.P == None or self.Q == None:
            P, Q = self.init_PQ()
            X = self.X
            W = self.build_weight_matrix(X)
            lI = np.identity(self.options['DIM']) * self.options['LAMBDA']

            for i in range(self.options['ITERATIONS']):
                logging.info('%d/%d iteration' % (i + 1,self.options['ITERATIONS']))
                P, Q = self.iteration(P, Q, W, X, lI)

                self.P, self.Q = P, Q
                self.save_model(iterations=i+1)
        else:
            logging.warn('Try to build already builded model, breaked')

    @timeit
    def iteration(self, P, Q, W, X, lI):
        P = self.new_P(P, Q, W, X, lI)
        Q = self.new_Q(P, Q, W, X, lI)

        return P, Q

    def new_Q(self, P, old_Q, W, X, lI):
        logging.info('start build Q')
        Q = sparse.csc_matrix(old_Q.shape)

        for i in range(Q.shape[1]):
            Q[:, i] = self.build_row(P, W[:, i].T, X[:, i].T, lI)

            if i % 1000 == 0:
                logging.info('%dth row of %d' % (i, Q.shape[1]))
        return Q

    def new_P(self, old_P, Q, W, X, lI):
        logging.info('start build P')
        P = sparse.csr_matrix(old_P.shape)

        for i in range(P.shape[1]):
            P[:, i] = self.build_row(Q, W[i, :], X[i, :], lI)

            if i % 1000 == 0:
                logging.info('%dth row of %d' % (i, P.shape[1]))
        return P

    def build_row(self, A, w_row, x_row, lI):
        """calc (A w_row A^T + lI)^-1 * A * w_row * x_row """
        w_row_len = max(w_row.shape)
        W_i = sparse.spdiags(w_row.A, 0, w_row_len, w_row_len)

        AW = A.dot(W_i)
        AWA = AW.dot(A.T)
        AWAl = AWA + lI
        AWAl_inv = sparse.csr_matrix(np.linalg.inv(AWAl))
        AWX = AW.dot(x_row.T)

        return AWAl_inv.dot(AWX)

    def apply(self):
        P = self.P
        Q = sparse.csr_matrix((self.options['DIM'], len(self.texts)))

        W = self.build_weight_matrix(self.X)
        X = self.X
        lI = np.identity(self.options['DIM']) * self.options['LAMBDA']

        Q = self.new_Q(P, Q, W, X, lI)
        return Q

    def build_weight_matrix(self, tf_idf_matrix):
        nnz_i, nnz_j, elems = sparse.find(tf_idf_matrix)
        value = np.zeros(elems.shape[0])
        value.fill(self.options['WM'])

        r = sparse.coo_matrix((value, (nnz_i, nnz_j)), shape=tf_idf_matrix.shape)
        return r.tocsr()

    def apply_to_dataset(self):
        log_and_print(logging.INFO, 'apply model to dataset')
        news_num = self.dataset.news.length()
        documents = self.dataset.get_documents()

        set_compare_vector(documents, self.Q)
        news, tweets = documents[:news_num], documents[news_num:]
        self.dataset_applied = (news, tweets)
