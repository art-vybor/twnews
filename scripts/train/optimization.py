import numpy as np
from scipy import sparse
from time import time    
from scipy.sparse.linalg import inv
import pickle
from twnews.utils.memoize import load


def build_weight_matrix(tf_idf_matrix):
    nnz_i, nnz_j, elems = sparse.find(tf_idf_matrix)
    value = np.zeros(elems.shape[0])
    value.fill(1e-2)

    r = sparse.coo_matrix((value, (nnz_i, nnz_j)), shape=tf_idf_matrix.shape)
    return r.tocsr()

corpus, tfidf = load('tf_idf_corpus')
lemmatized_texts = load('lemmatized_texts')

X = tfidf
W = build_weight_matrix(tfidf)
texts = lemmatized_texts
words = corpus


texts_num = len(texts)
words_num = len(words)
dim = 10
print texts_num, words_num

#init_model
P = np.random.rand(dim, words_num)
P = P*0.2-0.1
P = P.astype('float')
P = sparse.csr_matrix(P)
Q = np.random.rand(dim, texts_num)
Q = Q*0.2-0.1
Q = Q.astype('float')
Q = sparse.csr_matrix(Q)

iteration_num = 100
from multiprocessing import Pool

def get_new_P(old_P, Q, W, X, lI, threads):
    #print 'start build P'
    P = sparse.csr_matrix(old_P.shape)
    # data = [(Q, W[i, :], X[i, :], lI) for i in range(iteration_num)]
    #
    # res = Pool(threads).map(build_row1,data)
    # for i in range(iteration_num):
    #     P[:, i] = res[i]
    for i in range(1000):
        P[:, i] = build_row(Q, W[i, :], X[i, :], lI)

        if i % 1000 == 0:
            print '%dth iteration of %d' % (i, P.shape[1])

    return P


def build_row1((A, w_row, x_row, lI)):
    return build_row(A, w_row, x_row, lI)

import scipy
def build_row(A, w_row, x_row, lI):
    """calc (A w_row A^T + lI)^-1 * A * w_row * x_row """
    w_row_len = max(w_row.shape)
    W_i = sparse.spdiags(w_row.A, 0, w_row_len, w_row_len)

    AW = A.dot(W_i)
    AWA = AW.dot(A.T)

    AWAl = AWA + lI
    AWAl_inv = sparse.csr_matrix(np.linalg.inv(AWAl))
    AWX = AW.dot(x_row.T)

    return AWAl_inv.dot(AWX)

def iteration(P,Q,W,lI,threads):
    new_P = get_new_P(P, Q, W, X, lI, threads)
    new_Q = None
    return new_P,new_Q


for threads_num in [5]:
    print 'threads', threads_num
    start = time()
    lI = np.identity(dim) * 20
    iteration(P,Q,W, lI,threads=threads_num)
    end = time()
    print '\ttotal: %.2fs' % (end-start)
    print '\t100 iter: %.2fs' % ((end-start)/iteration_num*100)




        #from scipy import sparse
#     for i in range(20):
#         print 'start build P'
#         lW_i = list(W[i])
#         W_i = sparse.spdiags([lW_i], [0], len(lW_i), len(lW_i))
                
#         A = np.array(np.linalg.inv(np.dot(np.dot(Q,W_i),Q.T)+lI))
#Q_1 = sparse.csr_matrix(Q)