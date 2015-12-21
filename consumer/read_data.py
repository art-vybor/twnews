import json
d = open ('data').read()
for tweet in filter(None, d.splitlines()):
    try:
#    print tweet
        parsed_tweet = json.loads(tweet)
        text = parsed_tweet['text']
        time = parsed_tweet['created_at']
        print time, text.replace('\n', ' ')
    except Exception:
        pass


