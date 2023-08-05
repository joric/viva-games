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

# rewrite settings
settings = json.load(open('settings.json',encoding='utf-8'))
open(outdir+'/settings.js','w').write('var settings=\n'+json.dumps(settings,indent='  ')+';\n')

