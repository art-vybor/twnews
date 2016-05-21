import math
import logging
import numpy as np
from scipy import sparse

from collections import defaultdict
from twnews.timeit import timeit
from twnews.utils.memoize import memo_process, load, dump


def get_matrix_slice_by_column(M, indexes):
    length, width = M.shape

    #dim = len(corpus)

    data, row_idxs, column_idxs = [], [], []
    for column_idx, idx in enumerate(indexes):
        rows, _, values = sparse.find(M[:,idx])
        for i, value in enumerate(values):
            data.append(values[i])
            row_idxs.append(rows[i])
            column_idxs.append(column_idx)

    compare_matrix = sparse.csr_matrix((data, (row_idxs, column_idxs)), shape=(length, len(indexes)))
    return compare_matrix


def get_vector_length(v):
    idxs, _, value = sparse.find(v)
    sumxx = 0
    for i in idxs:
        x = v[(i,i)]
        sumxx += x*x
    return math.sqrt(sumxx*1.0)


def get_vectors_length_array(M):
    res = []
    for i in range(M.shape[1]):
        res.append(get_vector_length(M[:,i]))
    return res


class WTMF_G:
    def __init__(self,
                 texts,
                 corpus,
                 tf_idf_matrix,
                 links,
                 wm=1e-2,
                 dim=3,
                 iterations_num=1,
                 lmbd=20,
                 delta = 0.1,
                 try_to_load=False,
                 ):
        self.texts = texts
        self.words = corpus
        self.X = tf_idf_matrix
        self.wm = wm
        self.dim = dim
        self.iterations_num = iterations_num
        self.lmbd = lmbd
        self.delta = delta
        self.try_to_load=try_to_load
        self.P = None
        self.Q = None
        self.text_to_text = defaultdict(set)
        for i, j in links:
            self.text_to_text[i].add(j)
            self.text_to_text[j].add(i)

        self.model_filename = 'WTMFG_%s_%s' % (self.iterations_num, self.dim)
        if self.try_to_load:
            PQ_loaded = load(self.model_filename)
            if PQ_loaded:
                self.P, self.Q = PQ_loaded

    def __str__(self):
        return 'model(wm={wm}, dim={dim}, iter={iter}, lambda={lmbd}, texts={len_texts})'.format(
            wm=self.wm,
            dim=self.dim,
            iter=self.iterations_num,
            lmbd=self.lmbd,
            len_texts=len(self.texts),
        )

    def init_PQ(self):
        P = np.random.rand(self.dim, len(self.words))
        P = P * 0.2 - 0.1
        P = sparse.csr_matrix(P)

        Q = np.random.rand(self.dim, len(self.texts))
        Q = Q * 0.2 - 0.1
        Q = sparse.csr_matrix(Q)

        return P, Q

    def build(self):
        if self.P == None or self.Q == None:
            P, Q = self.init_PQ()
            X = self.X
            W = self.build_weight_matrix(X)
            lI = np.identity(self.dim) * self.lmbd

            for i in range(self.iterations_num):
                print '%d/%d iteration' % (i + 1, self.iterations_num)
                P, Q = self.iteration(P, Q, W, X, lI)

            dump((P, Q), self.model_filename)
            self.P, self.Q = P, Q
        else:
            logging.warn('Try to build already builded model, breaked')

    @timeit
    def iteration(self, P, Q, W, X, lI):
        #P = self.new_P(P, Q, W, X, lI)
        Q = self.new_Q(P, Q, W, X, lI)

        return P, Q

    def new_Q(self, P, old_Q, W, X, lI):
        print 'start build Q'
        Q = sparse.csc_matrix(old_Q.shape)
        Q_length = get_vectors_length_array(Q)

        for i in range(Q.shape[1]):
        #for i in range(100):
            Qi = Q[:,i]
            #print Qi.shape
            LQi = Q_length[i]
            #print LQi

            n_i = self.text_to_text[i]
            n_i.add(1)
            #print len(n_i)
            LQn_i = [Q_length[j] for j in n_i]
            #print len(LQn_i)

            Qn_i = get_matrix_slice_by_column(Q, n_i)
            #print Qn_i.shape
            Q[:, i] = self.build_relation_row(P, W[:, i].T, X[:, i].T, lI, Qi, LQi, Qn_i, LQn_i)

            if i % 1000 == 0:
                print '%dth iteration of %d' % (i, Q.shape[1])
        return Q

    def new_P(self, old_P, Q, W, X, lI):
        print 'start build P'
        P = sparse.csr_matrix(old_P.shape)

        #for i in range(P.shape[1]):
        for i in range(100):
            P[:, i] = self.build_row(Q, W[i, :], X[i, :], lI)

            if i % 1000 == 0:
                print '%dth iteration of %d' % (i, P.shape[1])
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

    def build_relation_row(self, A, w_row, x_row, lI, Qi, LQi, Qn_i, LQn_i):
        """calc (A w_row A^T + lI)^-1 * A * w_row * x_row """
        w_row_len = max(w_row.shape)
        W_i = sparse.spdiags(w_row.A, 0, w_row_len, w_row_len)

        AW = A.dot(W_i)
        AWA = AW.dot(A.T)
        AWAl = AWA + lI
        LQn_i_diag = sparse.spdiags(LQn_i, 0, len(LQn_i), len(LQn_i))
        coef_Q_diag_Q = self.delta * LQi ** 2 * Qn_i * LQn_i_diag * Qn_i.T
        AWAl_relation = AWAl + coef_Q_diag_Q.todense()
        AWAl_relation_inv = sparse.csr_matrix(np.linalg.inv(AWAl_relation))

        AWX = AW.dot(x_row.T)
        coef_Q_L = Qn_i * sparse.lil_matrix(LQn_i).T * self.delta * LQi
        AWX_relation = AWX + coef_Q_L

        return AWAl_relation_inv.dot(AWX_relation)

    def apply(self):
        P = self.P
        Q = sparse.csr_matrix((self.dim, len(self.texts)))

        W = self.build_weight_matrix(self.X)
        X = self.X
        lI = np.identity(self.dim) * self.lmbd

        Q = self.new_Q(P, Q, W, X, lI)
        return Q

    def build_weight_matrix(self, tf_idf_matrix):
        nnz_i, nnz_j, elems = sparse.find(tf_idf_matrix)
        value = np.zeros(elems.shape[0])
        value.fill(self.wm)

        r = sparse.coo_matrix((value, (nnz_i, nnz_j)), shape=tf_idf_matrix.shape)
        return r.tocsr()