import numpy as np
import glob
from PIL import Image
import sys, os
import csv
import math,random,json

target_image = Image.open('all-games.png')

basedir = 'images'

images = [*glob.glob(basedir + '/*')]
images.sort()

tw = 256
th = 192

n = len(images)

cw = 32768//tw
ch = n//cw

w = tw*cw
h = th*ch

x = 0
y = 0
dy = (w-h)//2

h = w

print('writing image %d x %d (%d tiles)' % (cw, ch, cw*ch))


def get_average(image):
    image = image.convert('RGB')
    im = np.array(image)
    w, h, d = im.shape
    avg =  (tuple(np.average(im.reshape(w * h, d), axis=0)))
    return avg

def get_colors(cname):
    colors = []
    if os.path.exists(cname):
        d = csv.DictReader(open(cname),delimiter='\t')
        for r in d:
            colors.append(r)
        return colors

    for i,fname in enumerate(images):
        im = Image.open(fname)
        avg = get_average(im)
        sys.stderr.write("Caching colors: %d of %d: %s...\r" % (i, len(images), avg))
        base = os.path.basename(fname)
        colors.append({'name':base, 'r':avg[0], 'g':avg[1], 'b':avg[2]})

    d = csv.DictWriter(open(cname,'w'), fieldnames=['name','r','g','b'], delimiter='\t')
    d.writeheader()
    for r in colors:
        d.writerow(r)

    return colors

def split_image(image, size):
    w, h = image.size
    cw, ch = size
    avgs = []
    x = y = 0

    for j in range(ch):
        for i in range(cw):

            x = int(i * w / cw)
            y = int(j * h / ch)

            left = x
            top = y
            right  = x + int(w/cw)
            bottom = y + int(h/ch)

            im = image.crop( (left, top, right, bottom) )

            avg = get_average(im)

            im.close()

            avgs.append(avg)

    return avgs

# -----------------

grid_size = (cw,ch)
target_colors = split_image(target_image, grid_size)
n = len(target_colors)

# loading_colors (delete colors.csv to re-cache for new images)
tile_colors = []
tiles_data = get_colors('colors.csv')
for c in tiles_data:
    v = tuple(map(float,[c['r'], c['g'], c['b']]))
    tile_colors.append(v)

grid_img = Image.new('RGB', (w, h))

target_set = set(range(len(target_colors)))
source_set = set(range(len(tile_colors)))

def find_best_match_random_target(target_colors, source_colors):
    best_source_index = -1
    best_dist = float("inf")

    target_index = random.choice(tuple(target_set))
    target_set.remove(target_index)

    best_target_index = target_index
    avg = target_colors[target_index]

    #if avg[0]==0 and avg[1]==0 and avg[2]==0:
    #    return target_index, -1

    for source_index in source_set:

        val = source_colors[source_index]

        dist = (abs(val[0] - avg[0]) +
                abs(val[1] - avg[1]) +
                abs(val[2] - avg[2]))

        if dist < best_dist:
            best_dist = dist
            best_source_index = source_index
            best_target_index = target_index

    source_set.remove(best_source_index)

    return best_target_index, best_source_index


random.seed(n) # deterministic seed to preseve name order for given size

names = ['']*n

for i in range(n):
    target_index, source_index = find_best_match_random_target(target_colors, tile_colors)

    if source_index<0 or target_index<0:
        continue

    name = tiles_data[source_index]['name']
    fname = basedir + '/'+name

    im = Image.open(fname)

    x = (target_index % cw) * tw
    y = dy + (target_index // cw) * th

    sys.stderr.write("Placing tile %d of %d (%d/%d)        \r" % (i, len(target_colors), target_index, source_index))

    grid_img.paste(im, (x, y))
    im.close()

    id = name.split('.')[0]
    names[target_index] = id


open('names.txt','w').write('\n'.join(names))
sys.stderr.write("Saving output file (%dx%d), please wait a few seconds...       \r" % (w,h))
grid_img.save('output.png')


