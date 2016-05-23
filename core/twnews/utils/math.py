import math
import numpy as np
from scipy import sparse


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