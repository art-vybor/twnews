import numpy as np
from scipy import sparse
from time import time    
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


def iteration(P,Q,W,lI):
    def build_row(A, w_row, x_row):
        '''calc (A w_row A^T + lI)^-1 * A * w_row * x_row '''
        W_i = sparse.spdiags(w_row, [0], len(w_row), len(w_row))

        AW = A.dot(W_i)

        AWA = AW.dot(A.T)

        AWAl = AWA + lI
        
        AWAl_inv = np.linalg.inv(AWAl) 

        AWX = AW.dot(x_row.T)
        
        return AWAl_inv.dot(AWX)

    new_P = P.copy()
    new_Q = Q.copy()    
    Q = sparse.csr_matrix(Q)
    P = sparse.csr_matrix(P)
        
    start = time()
    print 'start build P'
    for i in range(P.shape[1]):
        new_P[:,i] = build_row(Q, W[i,:], X[i,:])
        
        if i % 1000 == 0:
            print '%dth iteration of %d' % (i, P.shape[1])
    
    print 'start build Q'
    for j in range(Q.shape[1]):
        new_Q[:,j] = build_row(P, W[:,j], X[:,j])

        if j % 1000 == 0:
            print '%dth iteration of %d' % (j, Q.shape[1])

    end = time()    
    print 'time %s secs' % (end - start)
        
    return new_P,new_Q

l=20
lI = np.identity(dim)*l

for i in range(5):
    print '%d/%d' % (i, 5)
    P,Q = iteration(P,Q,W,lI)


with open('data/model/P', 'wb') as f:
    pickle.dump(P, f)

with open('data/model/Q', 'wb') as f:
    pickle.dump(Q, f)



        #from scipy import sparse
#     for i in range(20):
#         print 'start build P'
#         lW_i = list(W[i])
#         W_i = sparse.spdiags([lW_i], [0], len(lW_i), len(lW_i))
                
#         A = np.array(np.linalg.inv(np.dot(np.dot(Q,W_i),Q.T)+lI))
#Q_1 = sparse.csr_matrix(Q)