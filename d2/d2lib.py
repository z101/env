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

def d2re(rx, html, itr = True):
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

def d2html(url):
    hdrs= {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept": "*/*",
    }
    try: conn = opener.open(urllib2.Request(url, headers = hdrs))
    except urllib2.HTTPError, e: conn = e
    if conn.code == 200: return conn.read()
    else: raise Exception(conn)

def d2ajax(url, data, urldata = 0, method = "POST"):
    hdrs= {
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "*/*",
    }
    if urldata:
        request = urllib2.Request("{}?{}".format(url, urllib.urlencode(data)), headers = hdrs)
    else:
        request = urllib2.Request(url, headers = hdrs, data = urllib.urlencode(data))
    request.get_method = lambda: method
    try: conn = opener.open(request)
    except urllib2.HTTPError, e: conn = e
    if conn.code == 200: return json.loads(conn.read())
    else: raise Exception(conn)

def d2dbpath(fn):
    return os.path.join(os.path.expanduser("~"), ".d2db", fn)

def d2dbr(fn):
    fn = os.path.join(os.path.expanduser("~"), ".d2db", fn)
    with open(fn, "r") as f:
        return unicode(f.read(), 'utf-8')

def d2jdump(j):
    return json.dumps(j, indent = 2, ensure_ascii = False)
    
def d2dbw(fn, data):
    fn = os.path.join(os.path.expanduser("~"), ".d2db", fn)
    fdir = os.path.dirname(os.path.abspath(fn))
    if not os.path.exists(fdir):
        os.makedirs(fdir)
    with codecs.open(fn, "w+", "utf-8") as f:
        f.write(data)
