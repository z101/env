#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import json
import re
import os
import codecs

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()), urllib2.HTTPHandler())

def asre(rx, html, itr = True):
    l = []
    r = re.compile(rx, flags = re.U | re.I | re.S | re.M)
    if itr:
        for m in r.finditer(html):
            if len(m.groups()) > 0: l.append(m.groupdict())
            else: l.append(m.group(0))    
    else:
        for m in r.findall(html):
            l.append(m)    
    return l

def ashtml(url):
    hdrs= {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': '*/*',
    }
    try: conn = opener.open(urllib2.Request(url, headers = hdrs))
    except urllib2.HTTPError, e: conn = e
    if conn.code == 200: return unicode(conn.read(), 'utf-8')
    else: raise Exception(conn)

def asdbpath(fn):
    return os.path.join(os.path.expanduser('~'), '.asdb', fn)

def asdbr(fn):
    fn = os.path.join(os.path.expanduser('~'), '.asdb', fn)
    with open(fn, 'r') as f:
        return unicode(f.read(), 'utf-8')

def asjdumpu(j):
    return unicode(json.dumps(j, indent = 2, ensure_ascii = False), 'utf-8')

def asjdump(j):
    return json.dumps(j, indent = 2, ensure_ascii = False)
    
def asdbw(fn, data):
    fn = os.path.join(os.path.expanduser('~'), '.asdb', fn)
    fdir = os.path.dirname(os.path.abspath(fn))
    if not os.path.exists(fdir):
        os.makedirs(fdir)
    with codecs.open(fn, 'w+', 'utf-8') as f:
        f.write(data)
