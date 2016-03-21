# -*- coding: utf-8 -*-
import nltk
import string
from nltk.corpus import stopwords
from codecs import open

with open('english_text', 'r',  encoding='utf-8') as in_file:
    sample = in_file.read()

     
sentences = nltk.sent_tokenize(sample)

tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]

tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
for x in tagged_sentences:
    for y in x:
        print y[0],y[1]
    print '---'
chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

def extract_entity_names(t):
    entity_names = []
    
    if hasattr(t, 'node') and t.node:
        if t.node == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
                
    return entity_names

entity_names = []
for tree in chunked_sentences:
    # Print results per sentence
    # print extract_entity_names(tree)
    
    entity_names.extend(extract_entity_names(tree))

# Print all entity names
print entity_names

# Print unique entity names

    