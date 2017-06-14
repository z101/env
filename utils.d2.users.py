#!/usr/bin/python

import urllib2
import re
import random
from HTMLParser import HTMLParser
from time import sleep

def usrfromurl(url):
    m = re.search("^(?P<url>.*drive2.ru/users/(?P<usr>[^/\?]+))", url, flags = re.IGNORECASE)
    if m:
        return (m.group(2), m.group(1))

# {{{ google
def ugoogle():
    class upgoogle(HTMLParser):
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.urls = []
            self.isurl = False
            self.isnavtab = False
            self.iscur = False
            self.isnext = False
            self.nextpage = ""
            hdrs= {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            self.feed(urllib2.urlopen(urllib2.Request(url, headers=hdrs)).read())
        def handle_starttag(self, tag, attrs):
            attrs = dict((name.lower(), value) for name, value in attrs)
            if tag == "cite": self.isurl = True
            if tag == "table" and "id" in attrs and attrs["id"] == "nav":
                self.isnavtab = True
            if self.isnavtab and tag == "td":
                if "class" in attrs and attrs["class"] == "cur":
                    self.iscur = True
                elif self.iscur and not attrs:
                    self.iscur = False
                    self.isnext = True
                else:
                    self.iscur = False
            if self.isnext and tag == "a": self.nextpage = "https://www.google.ru" + attrs["href"]
        def handle_data(self, data):
            if self.isurl:
                u = usrfromurl(data)
                if u:
                    self.urls.append(u)
        def handle_endtag(self, tag):
            self.isurl = False
            if self.isnavtab and tag == "table": self.isnavtab = False
            if self.isnext and tag == "td": self.isnext = False
    print "parsing users from google"
    u = {}
    pc = 1
    print " - processing page {}".format(pc)
    sleep(random.randint(1, 5))
    p = upgoogle("https://www.google.ru/search?q=site%3Adrive2.ru+users+%D0%A0%D1%8F%D0%B7%D0%B0%D0%BD%D1%8C")
    uc = 0
    for usr, url in p.urls:
        if usr not in u:
            u[usr] = url
            uc += 1
    print "    * users: {}".format(len(uc)) 
    while p.nextpage:
        pc += 1
        print " - processing page {}".format(pc)
        sleep(random.randint(1, 5))
        p = upgoogle(p.nextpage)
        uc = 0
        for usr, url in p.urls:
            if usr not in u:
                u[usr] = url
                uc += 1
        print "    * users: {}".format(len(uc)) 
    return u
# }}}
        
u = {}
try:
    u.update(ugoogle())

    for usr, url in u.iteritems():
        print "{:<20} {}".format(usr, url)
except urllib2.HTTPError as e:
    print(e.headers)
    print(e.read())

