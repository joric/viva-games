import csv,json

lookup = {}
d = csv.reader(open('viva.csv',encoding='utf-8'),delimiter='\t')
for r in d:
    id,title,img,pub,genre = r[:5]
    pub = pub.replace('Издатель неизвестен','Unknown publisher')
    lookup[id] = [id,title,pub]

names = []

for name in open('names.txt').read().splitlines():
    names.append(lookup[name])

open('names.js','w').write('var names=\n'+json.dumps(names,indent='  ')+';\n')

