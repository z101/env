#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2
import re
import os
from HTMLParser import HTMLParser

def uhtml(html):
    u = {}
    for m in re.finditer("/users/(?P<usr>[^/\?\"\'\<]+)", html, flags = re.IGNORECASE):
        u[m.group("usr")] = "https://www.drive2.ru/users/" + m.group("usr")
    return u

def uread():
    u = {}
    for f in os.listdir(os.path.join(os.path.expanduser("~"), ".d2u/html")):
        with open(os.path.join(os.path.expanduser("~"), ".d2u/html", f)) as fh:
            u.update(uhtml(fh.read()))
    return u

def d2ajax():
#    <button class="c-button" data-action="subscription.more" data-type="userfollowers" data-id="288230376151730376" data-key="3BkmSy9c7E00Z_o7-qMFm6n44TFd5P06U8CHAw906qKX1xUwViFDaEvF47WgQM1ez8adiGyzw081WA5u2pr-5SiL-JwpOFCXUky9K5IH5F81qNKVrNA-p0vcSZAZFIROWgvGOB6I5mW0r4HSmNVyDVDpLYe8hblI7_0_abJLM2w8178yNt9vvW0-S6XVIiEs">Показать ещё</button>
    url = "https://www.drive2.ru/ajax/subscription"
    hdrs= {
        "Host": "www.drive2.ru",
        "Connection": "keep-alive",
#        "Content-Length": "316",
        "Origin": "https://www.drive2.ru",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "*/*",
        "Referer": "https://www.drive2.ru/",
#        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.8,ru;q=0.6",
#        "Cookie": ".AUI=_wfqzlwoyisJAAHmZh0lBQsDQL5BwPyR8j4kFs38ynBL1jmjlcOi; _AFF=2; _ym_uid=1493899634911634154; .CSY=1; .DVMI=Bo5cgEAAAAg; .PBIK=AgAAAAAAHCAmAQAAAAAGlfCAQAAFIAaXTYBAAAHuAAAAAAGQiio4jo5YZwclJ9BOd3ymUw-ftQ; .AMET=Cw6oiOGBrPeLbSs1BbdcWG3ZMGho0jCCl6XcTHwlMIz9wlp1pvALuxZE3FECWty-PcdAMX2EfnZcQu3Bjl41b3AFtLjWG9Ir7ltjGpX7r3I8bLc07Mzv1I4YsU91lPwi; .UTZ=1497624642 -180; _ym_isad=1; _ym_visorc_33911514=b; .DVAB=1; _ga=GA1.2.703470482.1493899633; _gid=GA1.2.189806629.1497624642",
    }
    aparams = {
        # const?
        ".FCTX": "_wfqzlwoyisTAAQRQnJ1LldlYi4xOjE4NDMyMzirMhF-koCMOQMffEwF2K9kvUchDA",
        # dummy?
        "_": "get",
        # data-type
        "type": "userfollowers",
        # data-key
        "key": "3BkmSy9c7E00Z_o7-qMFm6n44TFd5P06U8CHAw906qKX1xUwViFDaEvF47WgQM1ez8adiGyzw081WA5u2pr-5SiL-JwpOFCXUky9K5IH5F81qNKVrNA-p0vcSZAZFIROWgvGOB6I5mW0r4HSmNVyDVDpLYe8hblI7_0_abJLM2w8178yNt9vvW0-S6XVIiEs",
        # data-id
        "id": "288230376151730376"
    }
    method = "POST"
    handler = urllib2.HTTPHandler()
    opener = urllib2.build_opener(handler)
    data = urllib.urlencode(aparams)
    request = urllib2.Request(url, headers=hdrs, data=data)
    request.get_method = lambda: method
    try:
        connection = opener.open(request)
    except urllib2.HTTPError, e:
        connection = e
    if connection.code == 200:
        html = connection.read()
        print html
    else:
        raise Exception(connection)

d2ajax()
#
#Data
#
#.FCTX=_wfqzlwoyisTAAQRQnJ1LldlYi4xOjE4NDMyMzirMhF-koCMOQMffEwF2K9kvUchDA&_=get&type=userfollowers&key=3BkmSy9c7E00Z_o7-qMFm6n44TFd5P06U8CHAw906qKX1xUwViFDaEvF47WgQM1ez8adiGyzw081WA5u2pr-5SiL-JwpOFCXUky9K5IH5F81qNKVrNA-p0vcSZAZFIROWgvGOB6I5mW0r4HSmNVyDVDpLYe8hblI7_0_abJLM2w8178yNt9vvW0-S6XVIiEs&id=288230376151730376
#    pass

#u = uread()
#for usr, url in u.iteritems():
#    print "{:<20} {}".format(usr, url)
#print
#print "count", len(u)

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
