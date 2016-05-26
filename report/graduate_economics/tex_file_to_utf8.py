import re
import codecs

tex_filename='./tex/economics.tex'
res_filename='./tex/economics_utf8.tex'
#files from https://www.ctan.org/tex-archive/macros/latex/contrib/t2/enc-maps
t2cyr_filename = './t2cyr.txt'


cyr_to_utf_map = {}

with open(t2cyr_filename) as f:
    for line in f:
        splitted = line.split(';')
        utf_code = splitted[0]
        latex_cyr = splitted[1]
        if latex_cyr and utf_code:
            utf = unichr(int(utf_code, 16)).encode('utf-8')
            cyr_to_utf_map[latex_cyr] = utf


data = open(tex_filename).read()
data = data.replace('}\n{', '} {')


print 'checking...'
errors = 0
for cyr_letter, prefix in re.findall('\{(\\\\(cyr|CYR)\w+)\}', data, flags=0):
    #print cyr_letter
    if cyr_letter not in cyr_to_utf_map:
        errors += 1
    else:
        utf_codepoints = cyr_to_utf_map[cyr_letter]
        #print cyr_letter, utf_codepoints

print 'errors:', errors

if errors == 0:
    for cyr, utf in cyr_to_utf_map.items():
        data = data.replace('{%s}' % cyr, utf)
    data = unicode(data, 'utf-8')

    with codecs.open(res_filename, 'w', encoding='utf8') as f:
        f.write(data)

    print res_filename, 'successfully created'


