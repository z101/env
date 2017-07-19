#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re, json, operator, datetime, shutil
from aslib import asre
from aslib import asjdump
from aslib import asjdumpu
from aslib import ashtml
from aslib import asdbr
from aslib import asdbw
from aslib import asdbpath

fnum = 0

def asdata(path, title, rurl):
    def clean(text):
        return re.compile(u'\s\s+', flags = re.U).sub(
            ' ',
            re.compile(u'<.*?>', flags = re.U).sub(
                '',
                text.replace(u'<br/>', u'; ').replace(u'<br />', u'; ').replace(u'\r', u'').replace(u'\n', u'').replace(u'&nbsp;', ' ')
            )
        ).replace(u' ;', u';').strip()
    def asdatar(path, rurl):
        global fnum
        html = ashtml(rurl)
        r = u"""
\s+<td[^>]+>	
\s+<div class="category_name">
\s+<a[^>]+href="(?P<url>[^"]+)"> 
(?P<hname>.+?)
\s+</a>
\s+</div>
\s+<div class="category_description">
(?P<hdescr>.+?)</div>
\s+</td>
""".replace('\n', '\\n')
        ascats = asre(r, html)
        if len(ascats) == 0:
            asnop = asre(u'В данной категории нет товаров', html)
            if len(asnop) > 0:
                print u'  !!! WARNING: no products by link "{}"'.format(rurl)
                return
            asnav = asre(u'<span class="breadcrumbs pathway">.+?</span>', html)
            if len(asnav) == 0: raise Exception('breadcrumbs span not found')
            asnav = asnav[0]
            aslinks = asre(u'<a href="(?P<url>[^"]+)"[^>]+>\s*(?P<name>[^>]+)\s*</a>', asnav)
            if len(aslinks) == 0: raise Exception('breadcrumb links not found')
            asjs = {
                'cats': [],
                'prods': [],
            }
            for l in aslinks:
                if 'almerashop' in l['url'].lower():
                    url = l['url']
                else:
                    url = u'http://www.almerashop.ru{}'.format(l['url'])
                asjs['cats'].append({
                    'name': l['name'].strip(),
                    'url': url
                })
            ashdr = asre(u'<td[^>]+class="contentheading">(?P<name>[^>]+)</td>', html)
            if len(ashdr) == 0: raise Exception('header td not found')
            ashdr = ashdr[0]
            asjs['cats'].append({
                'name': ashdr['name'].strip(),
                'url': rurl
            })
            rcat = u' / '.join(c['name'] for c in asjs['cats']) 
            print u'getting products: [{}] "{}"'.format(str(fnum).zfill(4), rcat)
            html = ashtml(rurl)
            asplist = asre(u'<div id="product_list"', html)
            if len(asplist) == 0: raise Exception('products div not found')
            asplist = asre(u'<div id="product_list">[^<]*</div>', html)
            if len(asplist) > 0:
                print u'  !!! WARNING: empty category "{}"'.format(rcat)
                return
            html = ashtml('{}?limit=1000000&limitstart=0'.format(rurl))
            r = u"""<tr>
<td[^>]+><div class="product_name"[^>]+><a[^>]+href="(?P<url>[^"]+)">(?P<title>[^<]+)</a></div></td>
\s*<td[^>]+><div class="manufacturer_link"[^>]+>(?P<man>[^<]+)</div></td>
\s*<td[^>]+><div class="product_sku"[^>]+>(?P<sku>[^<]+)</div></td>
\s*<td[^>]+>(\s*<img[^>]+alt="(?P<mark>[^"]+)"[^>]+>\s*)?</td>
\s*<td[^>]+><div class="product_price"[^>]+>(?P<hprice>.+?)</div></td>
\s*<td[^>]+>(
\s*<form[^>]+>.+?</form>
)?\s*</td>
\s*<td><img src="(?P<img>[^"]+)"[^>]+></td>		
\s*</tr>""".replace('\n', '\\n')
            asprods = asre(r, html)
            if len(asprods) == 0: raise Exception('products not found')
            r = u'Результаты\s+(?P<from>\d+)\s+-\s+(?P<to>\d+)\s+из\s+(?P<all>\d+)'
            ascount = asre(r, html)
            if len(ascount) == 0:
                print u'  !!! WARNING: counters not found in "{}"'.format(rcat)
            else:
                ascount = ascount[0]
                expc = int(ascount['all'])
                if len(asprods) != expc: raise Exception('expected {} product(s), but found {}'.format(expc, len(asprods)))
            for p in asprods:
                asjs['prods'].append({
                    'url': p['url'],
                    'name': p['title'],
                    'man': p['man'],
                    'sku': p['sku'],
                    'mark': p['mark'],
                    'price': clean(p['hprice']),
                    'img': p['img'],
                })
            asdbw('{}/{}'.format(path, fnum), asjdump(asjs))
            fnum += 1
        else:
            for cat in ascats:
                asdatar(path, 'http://www.almerashop.ru{}'.format(cat['url']))
    global fnum
    fnum = 0
    hfpath = asdbpath(path)
    if os.path.isdir(hfpath) and os.path.exists(hfpath):
        print 'removing directory {}'.format(hfpath)
        shutil.rmtree(hfpath)
    print u'searching products: {}'.format(title)
    asdatar(path, rurl)
    print u'done.'

asdata('nac', u'Nissan Almera Classic', 'http://www.almerashop.ru/146-nissan-almera-classic.html')
asdata('amo', u'Амортизаторы KYB', 'http://www.almerashop.ru/278-amortizatory-kyb.html')
asdata('liq', u'Жидкости', 'http://www.almerashop.ru/391-zhidkosti.html')

#asdata('test', u'Test', 'http://www.almerashop.ru/432-shiny/diski.html')
