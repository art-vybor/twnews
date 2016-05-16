import pymorphy2
import unicodedata
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from polyglot.text import Text

from twnews.timeit import timeit


def detect_language(word):
    return 'russian' if 'CYRILLIC' in unicodedata.name(word[0]) else 'english'


def is_word(word):
    return word[0].isalpha()


def to_unicode(text):
    if not isinstance(text, unicode):
        return text.decode('utf-8')
    return text


class Lemmatizer():
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

    @timeit
    def split_texts_to_lemmas(self, texts):
        lemmas_list = map(self.split_text_to_lemmas, texts)
        return lemmas_list


@timeit
def lemmatize_texts(texts):
    lemmatizer = Lemmatizer()
    lemmas_list = lemmatizer.split_texts_to_lemmas(texts)
    return [' '.join(lemma) for lemma in lemmas_list]


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