#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json, codecs, datetime
from aslib import asdbpath
from aslib import asdbr
from aslib import asdbw

pcount = 0

def aspage(pn, hn, fltfirst = None, srt = None, fltlast = None):
    def cut(s):
        c = 2000
        return (s[:(c - 3)] + '...') if len(s) > c else s

    def wdata(f, path, ps):
        global pcount
        for i, pf in enumerate(ps):
            pj = json.loads(asdbr('{}/{}'.format(path, pf)))
            pth = u'&nbsp;/&nbsp;'.join(u'<a target="_blank" href="{}">{}</a>'.format(c['url'], c['name']) for c in pj['cats'])
            for i, p in enumerate(pj['prods']):
                pcount += 1
                f.write(u"""
    <tr>
        <td>{i}</td>
        <td>{code}</td>
        <td><img src="{img}" /></td>
        <td><a target="_blank" href="{url}">{name}</a></td>
%
        <td>{man}</td>
%
        <td>{sku}</td>
%
        <td>{mark}</td>
%
        <td>{price}</td>
%
        <td>{path}</td>
%
    </tr>
""".format(
    i = pcount,
    code = '{}.{}.{}'.format(path, pf, i),
    img = p['img'].replace('components/com_virtuemart/shop_image/product/Pirelli_Winter_I_5448bb34630ac.jpg', 'components/com_virtuemart/shop_image/product/resized/Pirelli_Winter_I_5448b443efc98_117x124.jpg'),
    url = u'http://www.almerashop{}'.format(p['url']),
    name = p['name'],
    man = p['man'],
    sku = p['sku'],
    mark = p['mark'] if p['mark'] is not None else '',
    price = p['price'],
    path = pth
))

    print u'generaring page "{}" - {}'.format(pn, hn)
    jnacpath = 'nac'
    jamopath = 'amo'
    jliqpath = 'liq'
    nacps = []
    if os.path.isdir(asdbpath(jnacpath)) and os.path.exists(asdbpath(jnacpath)): nacps = [int(fn) for fn in  os.listdir(asdbpath(jnacpath))]
    nacps.sort()
    amops = []
    if os.path.isdir(asdbpath(jamopath)) and os.path.exists(asdbpath(jamopath)): amops = [int(fn) for fn in  os.listdir(asdbpath(jamopath))]
    amops.sort()
    liqps = []
    if os.path.isdir(asdbpath(jliqpath)) and os.path.exists(asdbpath(jliqpath)): liqps = [int(fn) for fn in  os.listdir(asdbpath(jliqpath))]
    liqps.sort()
    if fltfirst is not None:
        nacps = fltfirst(nacps)
        amops = fltfirst(amops)
        liqps = fltfirst(liqps)
    if srt is not None:
        srt(nacps)
        srt(amops)
        srt(liqps)
    if fltlast is not None:
        nacps = fltlast(nacps)
        amops = fltlast(amops)
        liqps = fltlast(liqps)
    asdir = '/home/z101/repos/swerc/sites/default/as'
    if not os.path.exists(asdir):
        os.makedirs(asdir)
    page = os.path.join(asdir, '{}.tpl'.format(pn))
    with codecs.open(page, 'w+', 'utf-8') as f:
        f.write(u"""
<h3>{header}</h3>
<table>
    <tr>
        <th>#</th>
        <th>code</th>
        <th>img</th>
        <th>prod</th>
        <th>man</th>
        <th>sku</th>
        <th>mark</th>
        <th>price</th>
        <th>path</th>
    </tr>
%
""".format(header = hn))
        wdata(f, jnacpath, nacps)
        wdata(f, jamopath, amops)
        wdata(f, jliqpath, liqps)
        f.write(u'</table>')

# PAGES

aspage('all', 'AlmeraShop: All Products')
