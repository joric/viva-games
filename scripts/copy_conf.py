import csv,json,sys

outdir = "../tiles";

lookup = {}
d = csv.reader(open('viva.csv',encoding='utf-8'),delimiter='\t')
for r in d:
    id,title,img,pub,genre = r[:5]
    pub = pub.replace('Издатель неизвестен','Unknown publisher')
    lookup[id] = [id,title,pub]

names = []

for name in open('names.txt').read().splitlines():
    names.append(lookup[name])

open(outdir+'/names.js','w').write('var names=\n'+json.dumps(names,indent='  ')+';\n')

conf = json.load(open('conf.json',encoding='utf-8'))
open(outdir+'/conf.js','w').write('var conf=\n'+json.dumps(conf,indent='  ')+';\n')

