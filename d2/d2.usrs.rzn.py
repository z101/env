#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from d2lib import d2re
from d2lib import d2ajax
from d2lib import d2html
from d2lib import d2dbr
from d2lib import d2dbw

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
    
def d2usrsrzn():
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
    jcars = json.loads(d2dbr('cars'))
    print " - getting rzn car users"
    # debug
    #jcars = [{"car":"lada","name":u"Лада","models":[{"model":"m1506","name":"4x4 3D"}]}]
    # debug
    usrs = []
    for car in jcars:
        if "models" in car:
            for model in car["models"]:
                if "generations" in model:
                    for generation in model["generations"]:
                        print u'    * reading generation html: [{}] {} - {}'.format(car["name"], model["name"], generation["name"])
                        html = d2carhtml("https://www.drive2.ru/r/{}/{}/?city={}".format(car["car"], generation["generation"], rznid), rznid)
                        for u in d2re("/users/(?P<usr>[^/\?\"\'\<]+)", html):
                            if u["usr"] not in usrs:
                                usrs.append(u["usr"])
                else:
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
    d2dbw('usrs.rzn', "\n".join(usrs))
    
d2usrsrzn()
