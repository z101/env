#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re, json, operator
from d2lib import d2re
from d2lib import d2jdump
from d2lib import d2html
from d2lib import d2dbr
from d2lib import d2dbw
from d2lib import d2dbpath

def d2usrsrznsize():
    us = []
    path = 'usrs.rzn.html'
    ret = re.compile(u'<.*?>')
    res = re.compile(u'\s\s+')
    ft = lambda html : res.sub(' ', ret.sub('', html.replace("<br/>", "; ").replace("<br />", "; ").replace("\r", "").replace("\n", ""))).replace(" ;", ";").replace('&nbsp;', ' ').strip()
    ufs = os.listdir(d2dbpath(path))
    uc = len(ufs)
    for i, uf in enumerate(ufs):
        print 'processing {} from {}: {}'.format(i, uc, uf)
        upath = d2dbpath('{}/{}'.format(path, uf))
        html = d2dbr(upath)
        hdrs = []
        for hdr in d2re('\<h\d[^\>]*>(?P<hdr>.+?)\<\/h\d\>', html):
            hdr = unicode(hdr['hdr'], 'utf-8')
            if (hdr.lower() != u'представьтесь, пожалуйста'
                    and hdr.lower() != u'реклама'
                ):
                hdrs.append(ft(hdr))
        us.append({
            'usr': uf,
            'size': os.stat(upath).st_size,
            'headers': hdrs,
            })
    print 'writing size file'
    d2dbw('usrs.rzn.size', d2jdump(us))
    print 'done.'

def d2usrsrznheaders():
    uniquehdrs = set()
    for u in json.loads(d2dbr('usrs.rzn.size')):
        for hdr in u["headers"]:
            uniquehdrs.add(hdr)
    d2dbw('usrs.rzn.headers', u'\n'.join(uniquehdrs))
    print 'done.'

def d2usrsrzntop20size():
    us = dict()
    for u in json.loads(d2dbr('usrs.rzn.size')):
        us[u['usr']] = u['size']
    usort = sorted(us.items(), key = lambda x: (-x[1], x[0]))
    i = 0
    for k, v in usort:
        print '{} - {} [{}]'.format(i, k, v)
        i += 1
        if i >= 20: break
    print
    print 'done.'

def d2usrsrzndetails():
    usr = "pafs-777"
    udt = []
    html = d2dbr('usrs.rzn.html/{}'.format(usr))
    up = d2re((
        # user card
        u'\<div[^\>]+( |")c-user-card( |")[^\>]+\>(?P<ucard>.+?)'
        # counters
        u'\<div[^\>]+( |")c-user-info__nums[^\>]+\>(?P<counters>.+?)'
        # buttons
        u'\<div[^\>]+( |")c-user-info__buttons[^\>]+\>'
        # blog count
        u'.+?\<h\d[^\>]+\>.+?лог[^\<]+?\<span class="counter"\>(?P<cblog>\d+)'
        # cars
        u'.+?\<h\d[^\>]+\>.+?о..машин.+?\<div class="o-grid".+?(?P<cars>(\<div class="o-grid__item".+?\<div.+?\<div.+?\<\/div\>.+?\<div.+?\<div.+?\<\/div\>.+?\<div.+?\<\/div\>.+?\<div.+?\<\/div\>.+?\<div.+?\<\/div\>.+?\<\/div\>.+?\<\/div\>.+?\<\/div\>.+?)+)'
#        u''.format()
    ), unicode(html, 'utf-8'))[0]
    print up["cars"]
    ui = d2re((
        # user pic
        u'\<div.*?c-user-card__pic-container.*?<img.*?src="(?P<img>[^"]+)'
        # description
        u'.*?\<div.*?c-user-card__info[^\>]+\>(?P<rawdescr>.*?)\<\/div\>'
    ), up["ucard"])[0]
    uc = d2re((
        # counter followers
        u'\<a[^\>]+\>[^\<]*\<strong[^\>]*\>(?P<cfollowers>\d+)'
        # counter following
        u'.*?\<a[^\>]+\>[^\<]*\<strong[^\>]*\>(?P<cfollowing>\d+)'
        # counter following
        u'.*?\<a[^\>]+\>[^\<]*\<strong[^\>]*\>(?P<ccarfollowing>\d+)'
    ), up["counters"])[0]
    ret = re.compile(u'<.*?>')
    res = re.compile(u'\s\s+')
    ft = lambda html : res.sub(' ', ret.sub('', html.replace("<br/>", "; ").replace("<br />", "; ").replace("\r", "").replace("\n", ""))).replace(" ;", ";").strip()
    udt += {
        "img": ui["img"].replace("-200", "-100"),
        "usr": usr,
        "descr": ft(ui["rawdescr"]),
        "counters": {
            "blog": up["cblog"],
            "followers": uc["cfollowers"],
            "following": uc["cfollowing"],
            "carfollowing": uc["ccarfollowing"],
        }
    },
#    print json.dumps(udt, indent = 2, ensure_ascii = False)

#d2rznusrdetails()
#d2usrsrznsize()
#d2usrsrznheaders()
#d2usrsrzntop20size()
d2usrsrzndetails()
#print u'\u0411\u043b\u043e\u0433'.encode('utf-8')
