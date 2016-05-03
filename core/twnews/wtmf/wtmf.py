import numpy as np
from scipy import sparse

from twnews.timeit import timeit
from twnews.utils.memoize import memo_process


class WTMF:
    def __init__(self,
                 texts,
                 corpus,
                 tf_idf_matrix,
                 wm=1e-2,
                 dim=3,
                 iterations_num=1,
                 lmbd=20,
                 try_to_load=False,
                 ):
        self.texts = texts
        self.words = corpus
        self.X = tf_idf_matrix
        self.wm = wm
        self.dim = dim
        self.iterations_num = iterations_num
        self.lmbd = lmbd
        self.try_to_load=try_to_load
        self.P = None
        self.Q = None

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
        Q = np.random.rand(self.dim, len(self.texts))
        P = P * 0.2 - 0.1
        Q = Q * 0.2 - 0.1
        return P, Q

    def build(self):
        memo_filename = 'model_%s_%s' % (self.iterations_num, self.dim)
        self.P, self.Q = memo_process(lambda: self.build_PQ(), memo_filename, try_to_load=self.try_to_load)

    def build_PQ(self):
        P, Q = self.init_PQ()
        W = memo_process(lambda: self.build_weight_matrix(self.X), 'weights', try_to_load=self.try_to_load)
        X = np.array(self.X.todense())
        lI = np.identity(self.dim) * self.lmbd

        for i in range(self.iterations_num):
            print '%d/%d iteration' % (i + 1, self.iterations_num)
            P, Q = self.iteration(P, Q, W, X, lI)
        return P, Q

    @timeit
    def iteration(self, P, Q, W, X, lI):
        def build_row(A, w_row, x_row):
            """calc (A w_row A^T + lI)^-1 * A * w_row * x_row """
            w_row_len = max(w_row.shape)
            W_i = sparse.spdiags(w_row.A, 0, w_row_len, w_row_len)

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

            if i % 2000 == 0:
                print '%dth iteration of %d' % (i, P.shape[1])

        print 'start build Q'
        for j in range(Q.shape[1]):
            new_Q[:, j] = build_row(P, W[:, j].transpose(), X[:, j])

            if j % 2000 == 0:
                print '%dth iteration of %d' % (j, Q.shape[1])

        return new_P, new_Q

    def build_weight_matrix(self, tf_idf_matrix):
        nnz_i, nnz_j, elems = sparse.find(tf_idf_matrix)
        value = np.zeros(elems.shape[0])
        value.fill(self.wm)

        r = sparse.coo_matrix((value, (nnz_i, nnz_j)))
        return r.tocsr()
