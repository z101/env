#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import json
import re
import os
from HTMLParser import HTMLParser

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()), urllib2.HTTPHandler())

def d2re(rx, html):
    l = []
    for m in re.finditer(rx, html, flags = re.IGNORECASE):
        if len(m.groups()) > 0: l.append(m.groupdict())
        else: l.append(m.group(0))    
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

def d2cars():
    print " - getting car list"
    jcars = d2re("\<a[^\>]+href=\"/r/(?P<car>[^\"/]+)/?\"[^\>]*>(?P<name>[^\<]+)", d2html("https://www.drive2.ru/cars"))
    for crow in jcars:
        print ' - getting model list: "{}"'.format(crow["car"])
        jmodels = d2re("\<a[^\>]+class=\"c-link\"[^\>]+href=\"/r/{}/(?P<model>[^\"/]+)/?\"[^\>]*>(?P<name>[^\<]+)".format(crow["car"]), d2html("https://www.drive2.ru/r/{}".format(crow["car"])))
        if len(jmodels) > 0:
            print '    * models count: {}'.format(len(jmodels))
            crow["models"] = jmodels
    print "writing cars file"
    with open(os.path.join(os.path.expanduser("~"), ".d2u/cars"), "w+") as f:
        f.write(json.dumps(jcars, ensure_ascii = False))

def d2carhtml(url, cityid):
    def getpage(attrs, start, idx, cityid):
        return d2ajax("https://www.drive2.ru/ajax/carsearch.cshtml", {
            "context": attrs["data-context"],
            "start": start,
            "sort": attrs["data-sort"],
            "index": idx,
            "city": cityid,
            "country": attrs["data-country"],
        }, method = "GET", urldata = 1)
    html = d2html(url)
    battrs = d2re("\<button(?P<attrs>[^\>]+)\>\s*Показать\s+ещ", html)
    idx = 0
    ahtmls = []
    if len(battrs) > 0:
        attrs = dict((row["name"].lower(), row["value"]) for row in d2re("\s+(?P<name>[^\=]+)\s*\=\s*(\"|')(?P<value>[^\"']+)", battrs[0]["attrs"]))
        start = attrs["data-start"]
        jpage = getpage(attrs, start, idx, cityid)
        ahtmls.append(jpage["html"])
        idx += 1
        while "start" in jpage:
            jpage = getpage(attrs, jpage["start"], idx, cityid)
            ahtmls.append(jpage["html"])
            idx += 1
    html = unicode(html, "utf-8")
    return u"{}\n{}".format(html, u"\n".join(ahtmls))
    
def d2carusrsrzn():
    print " - getting rzn id"
    jcities = d2ajax("https://www.drive2.ru/ajax/geo.cshtml", {
        "_": "r",
        "token": "рязань",
    }, method = "GET", urldata = 1)
    rznid = ""
    for r in jcities[0]:
        if type(r) is dict:
            if (r["caption"].lower() == u'рязань'
                and r["country"].lower() == u'россия'
                and r["extra"].lower() == u'россия'):
                rznid = r["id"]
                break
    if not rznid: raise Exception("rzn id not found")
    print "    * rzn id: {}".format(rznid)
    print " - reading cars db"
    with open(os.path.join(os.path.expanduser("~"), ".d2u/cars"), "r") as f:
        jcars = json.loads(f.read())
    print " - getting rzn car users"
    # debug
    #jcars = [{"car":"lada","name":u"Лада","models":[{"model":"m1506","name":"4x4 3D"}]}]
    # debug
    usrs = []
    for car in jcars:
        if "models" in car:
            for model in car["models"]:
                print u'    * reading model html: [{}] {}'.format(car["name"], model["name"])
                html = d2carhtml("https://www.drive2.ru/r/{}/{}/?city={}".format(car["car"], model["model"], rznid), rznid)
                for u in d2re("/users/(?P<usr>[^/\?\"\'\<]+)", html):
                    if u["usr"] not in usrs:
                        usrs.append(u["usr"])
        else:
            print u'    * reading car html: [{}]'.format(car["name"])
            html = d2carhtml("https://www.drive2.ru/r/{}/?city={}".format(car["car"], rznid), rznid)
            for u in d2re("/users/(?P<usr>[^/\?\"\'\<]+)", html):
                if u["usr"] not in usrs:
                    usrs.append(u["usr"])
    print 
    print "count: {}".format(len(usrs))
    print "writing rzn users file"
    with open(os.path.join(os.path.expanduser("~"), ".d2u/rzn.users"), "w+") as f:
        f.write("\n".join(usrs))
    
#d2cars()
d2carusrsrzn()





#def uhtml(html):
#    u = {}
#    for m in re.finditer("/users/(?P<usr>[^/\?\"\'\<]+)", html, flags = re.IGNORECASE):
#        u[m.group("usr")] = "https://www.drive2.ru/users/" + m.group("usr")
#    return u
#
#def chtml(html):
#    u = {}
#    for m in re.finditer("/r/(?P<car>[^/\?\"\'\<]+)", html, flags = re.IGNORECASE):
#        u[m.group("usr")] = "https://www.drive2.ru/r/" + m.group("usr")
#    return u

def uread():
    u = {}
    for f in os.listdir(os.path.join(os.path.expanduser("~"), ".d2u/html")):
        with open(os.path.join(os.path.expanduser("~"), ".d2u/html", f)) as fh:
            u.update(uhtml(fh.read()))
    return u








def ufhtml(url):
    def gethtml(request):
        try:
            conn = opener.open(request)
        except urllib2.HTTPError, e:
            conn = e
        if conn.code == 200:
            return conn.read()
        else:
            raise Exception(conn)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()), urllib2.HTTPHandler())
    hdrs= {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept": "*/*",
    }
    html = gethtml(urllib2.Request(url, headers=hdrs))
    m = re.search('".FCTX",\s*"(?P<fctx>[^"]+)', html, flags = re.IGNORECASE)
    if not m:
        raise Exception("no .FCTX")
    fctx = m.group("fctx")
    m = re.search('\<button(?P<params>[^\>]+)\>Показать ещё', html, flags = re.IGNORECASE)
    if m:
        aparams = {
            ".FCTX": fctx,
            "_": "get",
        }
        for m in re.finditer("(?P<name>[^=]+)\s*=\s*(\"|')(?P<value>[^\"']+)", html, flags = re.IGNORECASE):
            if "data-type" in m.group("name"):
                aparams["type"] = m.group("value")
            if "data-key" in m.group("name"):
                aparams["key"] = m.group("value")
            if "data-id" in m.group("name"):
                aparams["id"] = m.group("value")

        url = "https://www.drive2.ru/ajax/subscription"
        hdrs= {
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Accept": "*/*",
        }
        request = urllib2.Request(url, headers=hdrs, data=urllib.urlencode(aparams))
        request.get_method = lambda: "POST"
        html = json.loads(gethtml(request))["html"]
        print html



#ufhtml("https://www.drive2.ru/users/rvalbi4/followers")

# ARCHIVE

# {{{ bing
def ubing():
    class upbing(HTMLParser):
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.iscur = False
            self.isnext = False
            self.nextpage = ""
            self.cpnum = -1
            hdrs= {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            self.html = urllib2.urlopen(urllib2.Request(url, headers=hdrs)).read() 
            self.feed(self.html)
        def handle_starttag(self, tag, attrs):
            attrs = dict((name.lower(), value) for name, value in attrs)
            if tag == "a" and "class" in attrs and attrs["class"] == "sb_pagS": self.iscur = True
            if self.iscur and tag == "a" and "aria-label" in attrs and " {}".format(int(self.cpnum) + 1) in attrs["aria-label"]:
                self.iscur = False
                self.isnext = True
            if self.isnext: self.nextpage = "https://www.bing.com" + attrs["href"]
        def handle_data(self, data):
            if self.iscur:
                self.cpnum = data
        def handle_endtag(self, tag):
            self.isnext = False
    def whtml(html, pc):
        with open(os.path.join(os.path.expanduser("~"), ".d2u/html/bing_{}.html".format(pc)), 'w+') as f:
            f.write(html)
    print "parsing users from bing"
    u = {}
    pc = 1
    print " - processing page {}".format(pc)
    p = upbing("https://www.bing.com/search?q=site%3Adrive2.ru+%D1%80%D1%8F%D0%B7%D0%B0%D0%BD%D1%8C+users")
    whtml(p.html, pc)
    while p.nextpage:
        pc += 1
        print " - processing page {}".format(pc)
        sleep(random.randint(5, 10))
        p = upbing(p.nextpage)
        whtml(p.html, pc)
# }}}
