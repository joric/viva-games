import csv
import os
import urllib.request
from PIL import Image
from collections import *
import io
import sys

basedir = 'images'
size=(256,192)

data = []
names = set()
lines = 0
noimg = 0
c = Counter()

if not os.path.exists(basedir):
    os.makedirs(basedir)

for s in csv.reader(open('viva.csv',encoding='utf-8'), delimiter='\t'):
    try:
        id,title,url,pub=s[:4]
    except ValueError as e:
        print(e, s)
        exit(0)
    lines += 1

    if 'game-no-image' in url:
        noimg += 1
        continue

    for key,ext in {'.gif-200x150.png':'.gif', '-200x150.png':'.png', '-200x150.gif':'.gif'}.items():
        if key in url:
            fname = basedir + '/' + id + ".png"
            url = url.replace(key, ext)

    data.append((id, fname, url, title))
    names.add(fname)
    c[fname] += 1

data.sort()

dup = sum(v for _,v in c.items() if v>1)
print('lines read %d, usable images %d, no-images: %d, duplicate images: %d' % (lines, len(names), noimg, dup))

existing = set([e.name for e in os.scandir(basedir)])
total = len(names)
count = len(existing)

for i, (id, fname, url, title) in enumerate(data):
    if os.path.exists(fname):
        continue
    req = urllib.request.Request(url, None, {'User-Agent':'megaparser'})

    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        #print('%s: name: %s url: %s' % (e, fname, url))
        continue

    buf = response.read()

    sys.stderr.write('writing file %d of %d %s\r' % (count, total, fname.ljust(60)))
    count += 1

    im = Image.open(io.BytesIO(buf))
    im = im.convert('RGB')
    if im.size != size:
        print('resizing', fname, 'to', size, 'was', im.size)
        if im.size==(320,240) or im.size==(384,288):
            im = im.crop((0,0,256,192))
        else:
            im = im.resize(size)

    b = io.BytesIO()
    im.save(b, 'png', optimize=True)
    buf = b.getvalue()

    f = open(fname,'wb')
    f.write(buf)
    f.close()
