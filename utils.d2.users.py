#!/usr/bin/python

import urllib2
from HTMLParser import HTMLParser

def ugoogle():
    class upgoogle(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.urls = []
            self.isurl = False
            url = "https://www.google.ru/search?q=site%3Adrive2.ru+users+%D0%A0%D1%8F%D0%B7%D0%B0%D0%BD%D1%8C"
            hdrs= {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            self.feed(urllib2.urlopen(urllib2.Request(url, headers=hdrs)).read())
        def handle_starttag(self, tag, attrs):
            if tag == "cite": self.isurl = True
        def handle_data(self, data):
            if self.isurl: self.urls.append(data)
        def handle_endtag(self, tag):
            self.isurl = False
    u = []
    u.extend(upgoogle().urls)
    return u
        
u = []
u.extend(ugoogle())

print '\n'.join(u)
