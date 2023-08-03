#!/usr/bin/env python3

import configparser,csv,sys,re,os,urllib.request,urllib.parse
from collections import defaultdict

def download(folder, url, encoding):
    global fp, current, total, visited
    if cached:=os.path.exists(fname:=os.path.join('download', folder, urllib.parse.quote_plus(url))):
        buf = open(fname,'rb').read()
    else:
        buf = urllib.request.urlopen(urllib.request.Request(url, None, {'User-Agent':'megaparser'})).read()
        if not os.path.exists(d:=os.path.dirname(fname)):
            os.makedirs(d)
        open(fname, "wb").write(buf)
    current += 1
    total = max(current, total)
    sys.stderr.write("Parsing file %d of %d (%s)...\r" % (current, total, 'cached' if cached else url))
    return buf.decode(encoding)

def replace(url, keys):
    for key,value in keys.items():
        if (substr:='{'+key+'}') in url:
            url = url.replace(substr, value)
    return url

def parse(config, folder, section, keys={}, content=''):
    opt, dd = config[section], defaultdict(dict)
    url, encoding = opt.get('url'),opt.get('encoding', 'utf-8')

    if alias:=opt.get('alias'):
        dd = defaultdict(dict)
        extra = []
        for key, regexp in config[folder +'.' + alias].items():
            c = 0
            for i,m in enumerate(re.finditer(regexp, content, re.MULTILINE | re.DOTALL)):
                if m.groups():
                    value = m.group(1)
                    dd[i][key] = value
                    c += 1
            if c == 0:
                extra.append(replace(regexp,keys))

        for i,d in dd.items():
            fp.write('\t'.join([*d.values()] + extra))
            fp.write('\n')

    url = replace(url, keys)
    if url in visited:
        return
    visited.add(url)
    content = download(folder, url, encoding)

    dd = defaultdict(dict)
    for key, regexp in opt.items():
        if key not in ('url','encoding','template','alias'):
            for i,m in enumerate(re.finditer(regexp, content, re.MULTILINE | re.DOTALL)):
                if m.groups():
                    value = m.group(1)
                    dd[i][key] = value

    for i,d in dd.items():
        keys.update(d)
        for key in d:
            #print('queued', folder + '.' + key, keys, url)
            parse(config, folder, folder + '.' + key, keys, content)


if __name__ == '__main__':
    config =  configparser.ConfigParser()
    config.read('megaparser2.ini', encoding='utf-8')
    folder = section = config.get('settings','default')
    fp = open(fname:=section+'.csv', 'w', encoding='utf-8')
    current = total = 0
    visited = set()
    if os.path.exists(d:='download/'+folder):
        total = len([*os.scandir(d)])
    parse(config, folder, section)
