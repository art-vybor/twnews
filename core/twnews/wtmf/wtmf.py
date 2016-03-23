from sklearn.feature_extraction.text import TfidfVectorizer


def create_tf_idf_matrix(texts, words):
    #return


def build_corpus(texts):
    corpus = set()
    pass

class WTMF:
    def __init__(self, texts):
        texts = texts
        #self.corpus = build_corpus(texts)
        self.X = TfidfVectorizer(texts) #create tf-idf matrix