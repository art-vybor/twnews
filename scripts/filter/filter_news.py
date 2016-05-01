from dateutil import parser as date_parser
import shelve

shelve_path = '/home/avybornov/rss.shelve'
dst_shelve_path = '/home/avybornov/twnews_data_april/rss.shelve'

s = shelve.open(shelve_path)
dst = shelve.open(dst_shelve_path)

for url in s:
    news = s[url]
    date = news['time']
    date = date_parser.parse(date)
    if 6 <= date.day and date.day <= 17:
        dst[url] = news
        dst.sync()