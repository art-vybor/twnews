import json
d = open ('../logs/ru').read()

for tweet in filter(None, d.splitlines()):
    try:
#    print tweet
        print tweet.decode('string_escape')
        #print time, text.replace('\n', ' ')
    except Exception as e:
        print e
        pass