#!/usr/bin/python
# -*- coding: utf-8 -*-

from d2lib import d2re
from d2lib import d2html
from d2lib import d2dbw
from d2lib import d2jdump

def d2cars():
    print " - getting car list"
    jcars = d2re("\<a[^\>]+href=\"/r/(?P<car>[^\"/]+)/?\"[^\>]*>(?P<name>[^\<]+)", d2html("https://www.drive2.ru/cars"))
    for crow in jcars:
        print ' - getting model list: "{}"'.format(crow["car"])
        jmodels = d2re("\<a[^\>]+class=\"c-link\"[^\>]+href=\"/r/{}/(?P<model>[^\"/]+)/?\"[^\>]*>(?P<name>[^\<]+)".format(crow["car"]), d2html("https://www.drive2.ru/r/{}".format(crow["car"])))
        if len(jmodels) > 0:
            print '    * models count: {}'.format(len(jmodels))
            crow["models"] = jmodels
            for mrow in jmodels:
                print ' - getting generation list: "{}"'.format(mrow["name"])
                jgens = d2re("\<a[^\>]+class=\"c-link\"[^\>]+href=\"/r/{}/(?P<generation>g[^\"/]+)/?\"[^\>]*>(?P<name>[^\<]+)".format(crow["car"]), d2html("https://www.drive2.ru/r/{}/{}".format(crow["car"], mrow["model"])))
                if len(jgens) > 0:
                    print '    * generations count: {}'.format(len(jgens))
                    mrow["generations"] = jgens
    print "writing cars file"
    d2dbw('cars', d2jdump(jcars))

d2cars()
