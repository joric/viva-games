import csv
import os
import urllib.request
from PIL import Image
import io
import sys

data = []

names = set()

basedir = 'gifs'

lines = 0
for s in csv.reader(open('viva.csv',encoding='utf-8'), delimiter='\t'):
    try:
        id,title,url,pub=s[:4]
    except ValueError as e:
        print(e, s)
        exit(0)
    lines += 1
    if '.gif-200x150.png' in url:
        fname = basedir + '/'+ id + '.gif'
        url = url.replace('gif-200x150.png','gif')
        data.append((id, fname, url, title))
        names.add(id+'.gif')
    elif '-200x150.png' in url: # must be rescaled png
        fname = basedir + '/' + id + '.gif'
        url = url.replace('-200x150.png','.png')
        data.append((id, fname, url, title))
        names.add(id+'.gif')
    elif 'game-no-image' not in url:
        fname = basedir + '/' + id + '.gif'
        url = url.replace('-200x150','')
        data.append((id, fname, url, title))
        names.add(id+'.gif')


data.sort()

print('lines read %d, usable names %d' % (lines, len(names)))

existing = set([e.name for e in os.scandir(basedir)])

total = len( names )
count = len( existing )

for i, (id, fname, url, title) in enumerate(data):
    if not os.path.exists(fname):
        req = urllib.request.Request(url, None, {'User-Agent':'megaparser'})

        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print('%s: name: %s url: %s' % (e, fname, url))
            continue

        buf = response.read()

        sys.stderr.write('writing file %d of %d %s\r' % (count, total, fname.ljust(60)))
        count += 1

        if url.endswith('.png'):
            im = Image.open(io.BytesIO(buf))
            im.thumbnail((256,192), Image.Resampling.NEAREST)

            palette = [
                0x00, 0x00, 0x00,
                0x00, 0x00, 0xd8,
                0x00, 0x00, 0xff,
                0xd8, 0x00, 0x00,
                0xff, 0x00, 0x00,

                0xd8, 0x00, 0xd8,
                0xff, 0x00, 0xff,
                0x00, 0xd8, 0x00,
                0x00, 0xff, 0x00,
                0x00, 0xd8, 0xd8,

                0x00, 0xff, 0xff,
                0xd8, 0xd8, 0x00,
                0xff, 0xff, 0x00,
                0xd8, 0xd8, 0xd8,
                0xff, 0xff, 0xff,

                0x00, 0x00, 0x00,
            ]

            p_img = Image.new('P', im.size)
            p_img.putpalette(palette)

            im = im.convert('RGB')

            im = im.quantize(palette=p_img, dither=0)

            b = io.BytesIO()
            im.save(b, 'gif')
            buf = b.getvalue()

        f = open(fname,'wb')
        f.write(buf)
        f.close()



