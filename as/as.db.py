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

def clean(text):
    return re.compile(u'\s\s+', flags = re.U).sub(
        ' ',
        re.compile(u'<.*?>', flags = re.U).sub(
            '',
            text.replace(u'<br/>', u'; ').replace(u'<br />', u'; ').replace(u'\r', u'').replace(u'\n', u'').replace(u'&nbsp;', ' ')
        )
    ).replace(u' ;', u';').strip()

def asdata(rurl):
    def asdatar(rurl, asjs, rcat = None):
        if (rcat is not None):
            print u'getting "{}" sub-categories'.format(rcat)
        else:
            print u'getting root categories'
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
            pass
        else:
            for cat in ascats:
                asjs.append({
                    'url': cat['url'],
                    'name': clean(cat['hname']),
                    'descr': clean(cat['hdescr']),
                    'cats': []
                })
                if (rcat is not None):
                    ncat = u'{} / {}'.format(rcat, asjs[-1]['name'])
                else:
                    ncat = asjs[-1]['name']
                asdatar('http://www.almerashop.ru{}'.format(cat['url']), asjs[-1]['cats'], ncat)
    asjs = []
    asdatar(rurl, asjs)

asdata('http://www.almerashop.ru/katalog-tovarov.html')

