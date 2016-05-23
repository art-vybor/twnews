# -*- coding: utf-8 -*-

import codecs
from polyglot.text import Text

with codecs.open('russian_text', 'r',  encoding='utf-8') as in_file:
    sample = in_file.read()


for row in filter(None, sample.splitlines()):
    blob = row
    text = Text(blob)
    text.language='ru'
    print row
    for entity in text.entities:
        print entity.tag, 
        for x in entity:
            print x,
        print ''