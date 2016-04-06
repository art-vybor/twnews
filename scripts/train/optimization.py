import numpy as np
from scipy import sparse
from time import time    
from scipy.sparse.linalg import inv
import pickle

with open('data/W', 'rb') as f:
    W = pickle.load(f)

with open('data/X', 'rb') as f:
    X = pickle.load(f)

with open('data/texts', 'rb') as f:
    texts = pickle.load(f)

with open('data/words', 'rb') as f:
    words = pickle.load(f)


print 'data loaded'

texts_num = len(texts)
words_num = len(words)
dim = 10
print texts_num, words_num

#init_model
P = np.random.rand(dim, words_num)
Q = np.random.rand(dim, texts_num)
P = P*0.2-0.1
Q = Q*0.2-0.1


X = np.array(X.todense())
print 'data generated'


def iteration(P,Q,W,l=20):

    new_P = P.copy()
    new_Q = Q.copy()
    
    lI = np.identity(dim)*l
    
    start = time()
    Q = sparse.csr_matrix(Q)
    #X = sparse.csr_matrix(X)
    print 'start build P'

    for i in range(1000):
        lW_i=W[i]
        W_i = sparse.spdiags(lW_i, [0], len(lW_i), len(lW_i))

        QW = Q.dot(W_i)

        QWQ = QW.dot(Q.T)

        QWQl = QWQ + lI
        
        QWQl_inv = np.linalg.inv(QWQl) 

        QWX = QW.dot(X[i,:].T)
        
        new_P[:,i] = QWQl_inv.dot(QWX)

    end = time()
    print 'time: %.2fs' % (end-start)

    return new_P,new_Q

start = time()
P,Q = iteration(P,Q,W)
end = time()
#print 'iteration: %.2fs' % (end-start)




        #from scipy import sparse
#     for i in range(20):
#         print 'start build P'
#         lW_i = list(W[i])
#         W_i = sparse.spdiags([lW_i], [0], len(lW_i), len(lW_i))
                
#         A = np.array(np.linalg.inv(np.dot(np.dot(Q,W_i),Q.T)+lI))
#Q_1 = sparse.csr_matrix(Q)