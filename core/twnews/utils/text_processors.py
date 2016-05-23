import itertools
import unicodedata
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

import pymorphy2
from polyglot.text import Text

from twnews.utils.extra import progressbar_iterate, timeit, multiprocess_map


def detect_language(word):
    return 'russian' if 'CYRILLIC' in unicodedata.name(word[0]) else 'english'


def is_word(word):
    return word[0].isalpha()


def to_unicode(text):
    if not isinstance(text, unicode):
        return text.decode('utf-8')
    return text


class Lemmatizer:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.wordnet_lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('russian') + stopwords.words('english'))

    def lemmatize(self, word):
        if detect_language(word) == 'russian':
            m_word = self.morph.parse(word)[0]
            return m_word.normal_form
        else:  # english
            return self.wordnet_lemmatizer.lemmatize(word)

    def split_text_to_lemmas(self, text):
        text = to_unicode(text)
        total_tokens = word_tokenize(text)
        word_tokens = filter(is_word, total_tokens)
        lemma_tokens = map(self.lemmatize, word_tokens)
        filtered_lemma_tokens = filter(lambda word: word not in self.stop_words, lemma_tokens)
        return filtered_lemma_tokens

    def split_text_to_lemmas_without_lemmatize(self, text):
        text = to_unicode(text)
        total_tokens = word_tokenize(text)
        word_tokens = filter(is_word, total_tokens)
        filtered_lemma_tokens = filter(lambda word: word not in self.stop_words, word_tokens)
        return filtered_lemma_tokens

    def split_texts_to_lemmas(self, texts):
        #lemmas_list = map(self.split_text_to_lemmas, progressbar_iterate(texts))
        lemmas_list = map(self.split_text_to_lemmas, texts)
        # lemmas_list = []
        # for i, text in progressbar_iterate(enumerate(texts)):
        #     lemmas_list.append(self.split_text_to_lemmas(text))
        return lemmas_list


#@timeit
def lemmatize_texts(texts):
    lemmatizer = Lemmatizer()
    lemmas_list = lemmatizer.split_texts_to_lemmas(texts)
    texts_list = [' '.join(lemmas) for lemmas in lemmas_list]
    return texts_list


@timeit
def lemmatize_texts_parallel(texts):
    return multiprocess_map(lemmatize_texts, texts)


@timeit
def build_tf_idf_matrix(texts, vocabulary=None):
    tvf = TfidfVectorizer(vocabulary=vocabulary)
    tfidf_matrix = tvf.fit_transform(texts)

    tfidf = tfidf_matrix.transpose()
    corpus = tvf.get_feature_names()

    return corpus, tfidf


def extract_entities(lemmatizer, text):
    t = Text(to_unicode(text))
    t.language = 'ru'

    result = set()
    for entity in t.entities:
        result.update([lemmatizer.lemmatize(x) for x in entity])
    return result