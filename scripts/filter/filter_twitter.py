from dateutil import parser as date_parser
from time import time
import shelve

shelve_path = '/home/avybornov/tweets.shelve'
dst_shelve_path = '/tmp/tweets_filtered.shelve'
#'/media/avybornov/FCBE4AD8BE4A8ADA/tweets_filtered.shelve'
keys_path = '/home/avybornov/tweets_keys'

s = shelve.open(shelve_path)
dst = shelve.open(dst_shelve_path)

total_keys = 24305129
rows_num = 1000*1000
i = 0

start = time()
with open(keys_path) as f:
    for key in f:
        #print line
        key = key[:-1]
        tweet = s[key]

        if tweet['lang'] != 'en':
            date = tweet['created_at']
            date = date_parser.parse(date)
            if 6 <= date.day and date.day <= 17:
                dst[key] = tweet
#            dst.sync()

        i+= 1
        if i % rows_num == 0:
            dst.sync()
            print '%s/%s %.2f%% (%.2fs elapsed)' % (i,total_keys, i*100.0/total_keys, time()-start)
            #break
dst.sync()
