#!/usr/bin/python
# -*- coding: utf-8 -*-

from d2lib import d2html
from d2lib import d2dbr
from d2lib import d2dbw

def d2usrsrznhtml():
    usrs = d2dbr('usrs.rzn').splitlines()
    uc = len(usrs)
    for i, usr in enumerate(usrs):
        print 'processing {} from {}: {}'.format(repr(i + 1), repr(uc), usr)
        d2dbw('usrs.rzn.html/{}'.format(usr), d2html('https://www.drive2.ru/users/{}'.format(usr)))
    print 'done.'
    
d2usrsrznhtml()
