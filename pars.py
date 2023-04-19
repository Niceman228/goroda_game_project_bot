import pprint


f = open('sityes.txt').readline()
d = [s.split('" class="image">')[0].replace('File:', '').replace('?uselang=ru','') for s in f.split('<a href="/') if ':' in s]


pprint.pprint(d[:100])

f2 = open('res.txt', 'a')
for i in d:
    f2.write(i + '\n')