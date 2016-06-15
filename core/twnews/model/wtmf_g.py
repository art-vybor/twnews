import numpy as np
from collections import defaultdict
from scipy import sparse

from twnews import defaults
from twnews.model.wtmf import WTMF
from twnews.utils.sparse_math import get_matrix_slice_by_column, get_vectors_length_array


class WTMF_G(WTMF):
    def __init__(self, dataset=None, options=defaults.DEFAULT_WTMFG_OPTIONS, model_name=None, dirname=defaults.TMP_FILE_DIRECTORY):
        super(WTMF_G, self).__init__(dataset, options, model_name, dirname=dirname)
        self.links = dataset.text_to_text_links

        self.text_to_text = defaultdict(set)
        for i, j in self.links:
            self.text_to_text[i].add(j)
            self.text_to_text[j].add(i)

    def name(self):
        return '{OLDNAME}_{DELTA}'.format(OLDNAME=super(WTMF_G, self).name(), DELTA=self.options['DELTA'])

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
                print '%dth row of %d' % (i, Q.shape[1])
        return Q

    def build_relation_row(self, A, w_row, x_row, lI, Qi, LQi, Qn_i, LQn_i):
        """calc (A w_row A^T + lI)^-1 * A * w_row * x_row """
        w_row_len = max(w_row.shape)
        W_i = sparse.spdiags(w_row.A, 0, w_row_len, w_row_len)

        AW = A.dot(W_i)
        AWA = AW.dot(A.T)
        AWAl = AWA + lI
        LQn_i_diag = sparse.spdiags(LQn_i, 0, len(LQn_i), len(LQn_i))
        coef_Q_diag_Q = self.options['DELTA'] * LQi ** 2 * Qn_i * LQn_i_diag * Qn_i.T
        AWAl_relation = AWAl + coef_Q_diag_Q.todense()
        AWAl_relation_inv = sparse.csr_matrix(np.linalg.inv(AWAl_relation))

        AWX = AW.dot(x_row.T)
        coef_Q_L = Qn_i * sparse.lil_matrix(LQn_i).T * self.options['DELTA'] * LQi
        AWX_relation = AWX + coef_Q_L

        return AWAl_relation_inv.dot(AWX_relation)