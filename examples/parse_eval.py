from collections import defaultdict

data = """
WTMF_G_(dataset_cutted_0.0)_90_1_0.01_1.95_0.001
recommendation
recommend dev by WTMF_G_(dataset_cutted_0.0)_90_1_0.01_1.95_0.001
recommendation
eval recommendation result
ATOP = 0.915044088299
RR = 0.388950308542
TOP10 = 0.488099344602
------------------------------------
WTMF_G_(dataset_cutted_0.0)_90_1_0.1_1.95_0.001
recommendation
recommend dev by WTMF_G_(dataset_cutted_0.0)_90_1_0.1_1.95_0.001
recommendation
eval recommendation result
ATOP = 0.950185444634
RR = 0.489585705754
TOP10 = 0.611935150052
------------------------------------
"""

data = open('/home/avybornov/git/twnews/examples/out1').read()
lines = filter(None, data.splitlines())
idx = 0

result = defaultdict(dict)

while idx < len(lines):
    header = lines[idx]
    idx += 7
    RR_line = lines[idx]
    idx += 1
    TOP1_line = lines[idx]
    idx += 1
    TOP3_line = lines[idx]
    idx += 2
    #dataset =  header.split('_')[3:5]
    print header
    #dim, iterations, lmbd, wm, delta = header.split('_')[5:]
    #dim, iterations, lmbd, wm = header.split('_')[4:]
    RR = RR_line.split()[-1][:6]
    TOP1 = TOP1_line.split()[-1][:6]
    TOP3 = TOP3_line.split()[-1][:6]

    #result[dim][iterations] = RR
    print RR, TOP1, TOP3

# for k, v in sorted(result[result.keys()[0]].items(), key=lambda x: int(x[0])):
#     print '& ' + k,
# print ' \\\\ \hline'
# for key, value in sorted(result.items(), key=lambda x: int(x[0])):
#     print key,
#     for k, v in sorted(value.items(), key=lambda x: int(x[0])):
#         print '& ' + v,
#     print ' \\\\ \hline'

# #print result
        
