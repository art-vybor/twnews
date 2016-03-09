# import json
# d = open ('data').read()
# for tweet in filter(None, d.splitlines()):
#     try:
# #    print tweet
#         parsed_tweet = json.loads(tweet)
#         text = parsed_tweet['text']
#         time = parsed_tweet['created_at']
#         print time, text.replace('\n', ' ')
#     except Exception:
#         pass

from datetime import datetime
import json
d = open('./logs/1457483094332').read()
out_file  = open('file', 'w')

tweets = {}

for tweet in filter(None, d.splitlines()):
    try:
#    print tweet
        parsed_tweet = json.loads(tweet)

        if 'delete' not in parsed_tweet:
            
            lang = parsed_tweet['lang']
            
            if lang in ['ru', 'en']:
                text = parsed_tweet['text'].encode('utf8').encode('string-escape')

                #retweeted = parsed_tweet['retweeted'] or text.startswith('RT @')
                time_ms = float(parsed_tweet['timestamp_ms'])/1000

                #print time, text.replace('\n', ' ')
                #print '<-----'
                out_file.write('%s %s\n' %(time_ms, text))

                # print retweeted
                # print time_ms
                # print len(text), text
                # print '----->'


    except Exception as e:
        print 'ERROR:', e
        pass


def parse_tweet(tweet):
    parsed_tweet = json.loads(tweet)

    if 'delete' not in parsed_tweet:
        
        lang = parsed_tweet['lang']
        
        if lang in ['ru', 'en']:
            text = parsed_tweet['text'].encode('utf8').encode('string-escape')

            #retweeted = parsed_tweet['retweeted'] or text.startswith('RT @')
            time_ms = float(parsed_tweet['timestamp_ms'])/1000

            #print time, text.replace('\n', ' ')
            #print '<-----'
            return '%s %s\n' %(time_ms, text)