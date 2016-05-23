import shelve
from itertools import chain
from tabulate import tabulate

from twnews import defaults
from twnews.resolver.resolver import get_domain


def url_analyse(resolve_path=defaults.RESOLVE_URL_MAP_PATH):
    resolve_map = shelve.open(resolve_path)

    res = {}
    count = 0
    # for url in urls:
    for url in resolve_map:
        full_url = resolve_map[url]
        domain = get_domain(full_url) if full_url else None

        if domain in res:
            res[domain].append(url)
        else:
            res[domain] = [url]

        count += 1

    print_result(res)


def print_result(res, top_size=25):
    total_rows = len(list(chain(*res.values())))
    print 'TOP%d by %d rows' % (top_size, total_rows)
    sorted_res = sorted(res.items(), key=lambda x: len(x[1]), reverse=True)

    sum_percent = 0
    table = []
    for domain, count in sorted_res[:top_size]:
        percent = len(count)*100.0/total_rows
        #print '%s\t%s\t%.2f%%' % (domain, len(count), percent)#, count
        if not domain:
            domain = 'ERROR'
        table.append((domain, len(count), '%.02f' % percent))
        sum_percent+=percent

    print tabulate(table)

    print 'total_percent in TOP%s: %.2f' % (top_size, sum_percent)
    print '--------------------------------------'