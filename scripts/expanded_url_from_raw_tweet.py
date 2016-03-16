import json
rows = open('/home/avybornov/logs/raw_tweets').read().split('\n')
#print rows[:10]
tweets = map(json.loads, filter(None, rows))

tweets = tweets[:10]

for tweet in tweets:
    if 'delete' not in tweet:        
        lang = tweet['lang']        
        if lang in ['ru']:
            retweet = False
            text = tweet['text']
            if 'retweeted_status' in tweet: #tweet retweeted
                text = tweet['retweeted_status']['text']
                retweet = True
            text = text.encode('utf8').encode('string-escape')
            created_at = tweet['created_at']
            #time_ms = float(parsed_tweet['timestamp_ms'])/1000

            print retweet
            print tweet['text'].replace('\n', ' ')
            #print #text.decode('string-escape')
            print tweet['entities']['urls']

#print tweets[0]