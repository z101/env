#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json, codecs, datetime
from d2lib import d2dbpath
from d2lib import d2dbr
from d2lib import d2dbw

def upage(pn, hn, fltfirst = None, srt = None, fltlast = None):
    def cut(s):
        c = 2000
        return (s[:(c - 3)] + '...') if len(s) > c else s

    print u'generaring page "{}" - {}'.format(pn, hn)
    jsonpath = 'usrs.rzn.json'
    us = os.listdir(d2dbpath(jsonpath))
    if fltfirst is not None:
        us = fltfirst(us)
    if srt is not None:
        srt(us)
    if fltlast is not None:
        us = fltlast(us)
    d2dir = '/home/z101/repos/swerc/sites/default/d2'
    if not os.path.exists(d2dir):
        os.makedirs(d2dir)
    page = os.path.join(d2dir, '{}.tpl'.format(pn))
    with codecs.open(page, 'w+', 'utf-8') as f:
        f.write(u"""
<h3>{header}</h3>
<table>
    <tr>
        <th>#</th>
        <th>ava</th>
        <th>img</th>
        <th>usr</th>
        <th>descr</th>
        <th>about</th>
        <th>stats</th>
        <th>rdate</th>
        <th>cnt</th>
        <th>cars</th>
        <th>cmu</th>
    </tr>
%
""".format(header = hn))
        for i, u in enumerate(us):
            u = json.loads(d2dbr('usrs.rzn.json/{}'.format(u)))
            f.write(u"""
    <tr>
        <td>{i}</td>
        <td><img src="{aimg}" /></td>
        <td><img src="{img}" /></td>
        <td><a target="_blank" href="https://www.drive2.ru/users/{usr}">{nameu}</a></td>
%
        <td>{descr}</td>
%
        <td>{about}</td>
%
        <td>{stats}</td>
%
        <td>{rdate}</td>
        <td>
            B&nbsp;{cblog}&nbsp;<br />
            F&nbsp;<span style="color:red;">{cfollowers}</span>&nbsp;<br />
            C&nbsp;{ccfollowing}&nbsp;<br />
            U&nbsp;{cfollowing}&nbsp;<br />
        </td>
%
        <td>{cars}</td>
%
        <td>{cmu}</td>
%
    </tr>
""".format(
    i = (i + 1),
    aimg = u['aimg'].replace('960.jpg', '120.jpg'),
    img = u['img'].replace('200.jpg', '100.jpg'),
    usr = u['usr'],
    nameu = u['nameu'],
    descr = cut(u['descr']),
    about = cut(u['about']),
    stats = cut(u['stats']),
    rdate = u['rdate'].replace('-', '&#8209;'),
    cblog = u['counters']['blog'],
    cfollowers = u['counters']['followers'],
    ccfollowing = u['counters']['carfollowing'],
    cfollowing = u['counters']['following'],
    cars = u"""
<table style="border:0">
{}
</table>
""".format(''.join(u"""
<tr>
    <td style="border:0"><img src="{img}" /></td>
    <td style="border:0"><a {former} target="_blank" href="https://www.drive2.ru{url}">{name}</a></td>
    <td style="border:0"><span style="color:red">{drive}</span>/{cblog}</td>
</tr>
%
""".format(
    img = car['img'].replace('960.jpg', '80.jpg').replace('480.jpg', '80.jpg'),    
    name = car['name'],
    url = car['url'],
    drive = car['drive'],
    cblog = car['cblog'],
    former = 'style="color:gray"' if car['former'] == '1' else ''
) for car in u['cars'])),
    cmu = u'<ul>{}</ul>'.format(''.join(u"""
<li><a target="_blank" href="{url}" {sadm}>{name}{nadm}</a></li>
%
""".format(
    name = c['name'],
    url = c['url'],
    nadm = ' (adm)' if c['adm'] == '1' else '',
    sadm = 'style="color:red"' if c['adm'] == '1' else '',
) for c in u['communities'])),
))
        f.write(u'</table>')

def ru(u):
    return json.loads(d2dbr('usrs.rzn.json/{}'.format(u)))

# PAGES

def hasnac(u):
    u = ru(u)
    cars = u''.join(c['name'] for c in u['cars']).lower()
    return ('almera' in cars and 'classic' in cars)

#upage(
#    'uflw',
#    'Ryazan Users: Max Followers',
#    srt = lambda us: us.sort(key = lambda u: int(ru(u)['counters']['followers']), reverse = True),
##    fltlast = lambda us: us[:500],
#)

upage(
    'ulast',
    'Ryazan Users: Last 50',
    srt = lambda us: us.sort(key = lambda u: datetime.datetime.strptime(ru(u)['rdate'], '%Y-%m-%d'), reverse = True),
    fltlast = lambda us: us[:50],
)

upage(
    'unac',
    'Ryazan Users: Nissan Almera Classic',
    fltfirst = lambda us: filter(lambda u: hasnac(u), us),
    srt = lambda us: us.sort(key = lambda u: int(ru(u)['counters']['followers']), reverse = True),
)

# Что еще поискать:
# vk.com, vk.ru, vkontakte.ru, вконтакте
# клуб, club
# youtube, ютуб, блог
# instagram
# IT
# гаражи
# радио
# мажоры
# спорт, автоспорт, автокросс
# работа, работаю
# продаю, продажа
# www, .ru
# кулибин, kulibin
# можно поискать по возрасту
# студия, магазин, сервис
# выбрать все машины, посмотреть редкие марки
# СССР
# Custom, tuning, тюнинг, усовершенст, модерн
# проект
# выделить имена и фамилии
