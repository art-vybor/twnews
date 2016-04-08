from scipy import spatial
from time import time
from sklearn.metrics.pairwise import cosine_similarity
import math


x = [3.0, 45, 7, 2.0]
y = [2, 54.2, 13.1, 15]


def spatial_distanse(x, y):
    return 1 - spatial.distance.cosine(x,y)


def pairwise(x,y):
    return cosine_similarity(x,y)[0][0]


def custom(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)



def test(f, x, y):
    start = time()
    for _ in range(1000):
        res = f(x,y)
    end = time()
    #print f(x, y)
    print '%s: %ss' % (f.__name__, end-start)


test(spatial_distanse, x, y)
test(pairwise, x, y)
test(custom, x, y)
test(custom1, x, y)
