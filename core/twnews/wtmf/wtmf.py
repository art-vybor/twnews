from sklearn.feature_extraction.text import TfidfVectorizer

from twnews.wtmf.text_processors import Lemmatizer

def create_tf_idf_matrix(texts, words):
    pass
    #return


def build_corpus(texts):
    corpus = set()
    pass

class WTMF:
    def __init__(self, texts):
        self.texts = texts

    def build(self):
        # lemmatize
        lemmatizer = Lemmatizer()
        lemmas_list = lemmatizer.split_texts_to_lemmas(self.texts)
        texts = [' '.join(lemma) for lemma in lemmas_list]

        # build X and corpus
        tvf = TfidfVectorizer()
        tfidf_matrix = tvf.fit_transform(texts)
        X = tfidf_matrix.transpose()
        corpus = tvf.get_feature_names()
