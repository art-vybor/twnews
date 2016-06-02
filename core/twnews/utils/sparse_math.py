import math
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity as matrix_cosine_similarity


def cosine_similarity(v1,v2):
    """fast cosine similarity for sparse vectors"""

    v1_idxs, _, value = sparse.find(v1)
    v2_idxs, _, value = sparse.find(v2)

    sumxx, sumxy, sumyy = 0, 0, 0
    for i in set(np.append(v1_idxs, v2_idxs)):
        x = v1[(i,0)]; y = v2[(i,0)]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)


def get_matrix_slice_by_column(M, indexes):
    length, width = M.shape

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


def get_similarity_matrix(documents_1, documents_2, corpus, tf_idf_matrix):
    def convert_to_compare_matrix(documents):
        dim = len(corpus)

        data, row_idxs, column_idxs = [], [], []
        for column_idx, document in enumerate(documents):
            rows, _, values = sparse.find(tf_idf_matrix[:, document.index])
            for i, value in enumerate(values):
                data.append(values[i])
                row_idxs.append(rows[i])
                column_idxs.append(column_idx)

        compare_matrix = sparse.csr_matrix((data, (row_idxs, column_idxs)), shape=(dim, len(documents)))
        return compare_matrix

    matrix_1 = convert_to_compare_matrix(documents_1)
    matrix_2 = convert_to_compare_matrix(documents_2)
    mat = matrix_cosine_similarity(matrix_1.T, matrix_2.T)

    return mat