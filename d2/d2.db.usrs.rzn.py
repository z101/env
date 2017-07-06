#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re, json, operator, datetime, shutil
from d2lib import d2re
from d2lib import d2jdump
from d2lib import d2html
from d2lib import d2dbr
from d2lib import d2dbw
from d2lib import d2dbpath

def d2usrsrzndetails():
    def clean(text):
        return re.compile(u'\s\s+', flags = re.U).sub(
            ' ',
            re.compile(u'<.*?>', flags = re.U).sub(
                '',
                text.replace(u'<br/>', u'; ').replace(u'<br />', u'; ').replace(u'\r', u'').replace(u'\n', u'').replace(u'&nbsp;', ' ')
            )
        ).replace(u' ;', u';').strip()
    def hasheader(h, html):
        return len(d2re(u'<h\d+[^>]+>[^<]*{}'.format(h), html, False)) > 0
    def uinfo(usr, html):
        u = {}
        r = u"""
        <div class="c-user-card c-user-card--h c-user-card--main c-user-info__user" itemscope itemtype="http://schema.org/Person">
            <div class="c-user-card__pic-container">
                <div class="c-user-card__pic"><a href="[^"]+"><img src="(?P<img>[^"]+)" width="200" height="200" itemprop="image" alt=""></a></div>
            </div>
            <div class="c-user-card__body">
                <h1 class="c-header-main c-user-card__username">
                    <span class="c-user-card__username-url">
                        <a class="c-link c-link--white c-username" href="[^"]+" itemprop="url"><span itemprop="name">(?P<nameu>[^<]+)</span></a>
.+?
                </h1>
                <div class="c-user-card__info">
(?P<hdescr>.+?)
                </div>
            </div>
        </div>

        <div class="o-ibc c-user-info__nums">
            <a class="c-round-num-block c-round-num-block--followers" href="[^"]+"><strong id="user-followers">(?P<cfollowers>\d+)</strong> <span id="user-followers-legend">Читател[^<]+</span></a>
            <a class="c-round-num-block" href="[^"]+"><strong>(?P<cfollowing>\d+)</strong> <span>Челове[^<]+<br />читает</span></a>
            <a class="c-round-num-block" href="[^"]+"><strong>(?P<ccarfollowing>\d+)</strong> <span>Маши[^<]+<br />читает</span></a>
        </div>
""".replace('\n', '\\r\\n')
        ucard = d2re(r, html)
        if len(ucard) == 0: raise Exception('ucard not found')
        ucard = ucard[0]
        cblog = '0'
        if hasheader(u'Блог {}'.format(ucard['nameu']), html):
            r = u"""
</form>        <h3 class="c-header c-header-floating">Блог {}&nbsp;<span class="counter">(?P<cblog>\d+)</span></h3>
""".replace('\n', '\\r\\n').format(ucard['nameu'])
            ucblog = d2re(r, html)
            if len(ucblog) == 0: raise Exception('ucblog not found')
            cblog = ucblog[0]['cblog']
        # about
        r = u"""
(        <h3 class="c-header-side">Обо мне</h3>
            <div class="o-grid-row">
                <a class="c-lightbox-anchor js-lightbox" href="(?P<aimg>[^"]+)" data-size="[^"]+" itemscope itemtype="http://schema.org/ImageObject">
<div class="o-img"[^>]+><span style="[^"]+"></span><img src="[^"]+" width="[^"]+" height="[^"]+" itemprop="contentUrl"></div>
                </a>
            </div>
)?(            <div class="user-about text text--xs">
(?P<habout>.+?)</div>
)?    <div class="c-ministats">

        <div class="c-ministats__item">
            <span data-tt="[^\d]+(?P<rdd>\d+)\s(?P<rdm>[^\s"]+)\s?(?P<rdy>\d+)?">[^<]+</span>
        </div>
            <div class="c-ministats__item">
(?P<hstats>.+?)
            </div>
""".replace('\n', '\\r\\n')
        uabout = d2re(r, html)
        if len(uabout) == 0: raise Exception('uabout not found')
        uabout = uabout[0]
        rdm = 0
        if u'янва' in uabout['rdm']: rdm = 1
        elif u'февра' in uabout['rdm']: rdm = 2
        elif u'март' in uabout['rdm']: rdm = 3
        elif u'апрел' in uabout['rdm']: rdm = 4
        elif u'мая' in uabout['rdm']: rdm = 5
        elif u'июн' in uabout['rdm']: rdm = 6
        elif u'июл' in uabout['rdm']: rdm = 7
        elif u'авгус' in uabout['rdm']: rdm = 8
        elif u'сентяб' in uabout['rdm']: rdm = 9
        elif u'октяб' in uabout['rdm']: rdm = 10
        elif u'нояб' in uabout['rdm']: rdm = 11
        elif u'декаб' in uabout['rdm']: rdm = 12
        else: raise Exception('uabout: unknown month {}'.format(uabout['rdm']))
        rdy = datetime.datetime.now().year
        if not uabout['rdy'] is None:
            rdy = int(uabout['rdy'])
        rdt = datetime.date(rdy, rdm, int(uabout['rdd']))
        aimg = ''
        if not uabout['aimg'] is None:
            aimg = uabout['aimg']
        about = ''
        if not uabout['habout'] is None:
            about = clean(uabout['habout'])
        u.update({
            'img': ucard['img'].replace('-200', '-100'),
            'usr': usr,
            'descr': clean(ucard['hdescr']),
            'aimg': aimg.replace('-960', '-120'),
            'about': about,
            'rdate': str(rdt),
            'stats': clean(uabout['hstats']),
            'counters': {
                'blog': cblog,
                'followers': ucard['cfollowers'],
                'following': ucard['cfollowing'],
                'carfollowing': ucard['ccarfollowing'],
            }
        })
        return u
    recar = u'\<div class="o-grid__item".+?\<div.+?\<div.+?\<\/div\>.+?\<div.+?\<div.+?\<\/div\>.+?\<div.+?\<\/div\>.+?\<div.+?\<\/div\>.+?\<div.+?\<\/div\>.+?\<\/div\>.+?\<\/div\>.+?\<\/div\>'
    def ucars(html):
        cars = []
        if hasheader(u'Мои машины', html):
            ucars = d2re((
                # cars
                u'\<h\d[^\>]+\>.+?Мои машины.+?<div class="o-grid".+?(?P<cars>(\s+{cars})+)'
                # params
                .format(cars = recar)
            ), html)
            if (len(ucars)) == 0: raise Exception('ucars are not found')
            ucars = ucars[0]
            for m in d2re(recar, ucars['cars'], False):
                ucar = d2re((
                    # img 
                    u'\<img src="(?P<img>[^"]+)'
                    # url & name
                    u'.+?\<a class="c-car-title[^\>]+href="(?P<url>[^"]+)"[^\>]*\>(?P<name>[^\<]+)'
                    # blog count
                    u'.+?\<span class="counter[^\>]+\>(?P<cblog>[^\<]+)'
                ), m)
                if (len(ucar)) == 0: raise Exception('ucar details is not found')
                ucar = ucar[0]
                cars.append({
                    'name': ucar['name'],
                    'img': ucar['img'].replace("-480", "-80"),
                    'url': ucar['url'],
                    'cblog': ucar['cblog'],
                    'former': '0',
                })
        return cars
    def ucar(html):
        car = []
        if hasheader(u'Моя машина', html):
            ucar = d2re((
                # car
                u'\<h\d[^\>]+\>.+?Моя машина.+?<div class="o-grid".+?(?P<car>(\s+{car})+)'
                # params
                .format(car = recar)
            ), html)
            if (len(ucar)) == 0: raise Exception('ucar are not found')
            ucar = ucar[0]
            for m in d2re(recar, ucar['car'], False):
                ucar = d2re((
                    # img 
                    u'\<img src="(?P<img>[^"]+)'
                    # url & name
                    u'.+?\<a class="c-car-title[^\>]+href="(?P<url>[^"]+)"[^\>]*\>(?P<name>[^\<]+)'
                    # blog count
                    u'.+?\<span class="counter[^\>]+\>(?P<cblog>[^\<]+)'
                ), m)
                if (len(ucar)) == 0: raise Exception('ucar details is not found')
                ucar = ucar[0]
                car.append({
                    'name': ucar['name'],
                    'img': ucar['img'].replace("-480", "-80"),
                    'url': ucar['url'],
                    'cblog': ucar['cblog'],
                    'former': '0',
                })
        return car
    def ucarsformer(html):
        cars = []
        if hasheader(u'Мои бывшие', html):
            ucars = d2re((
                # cars
                u'\<h\d[^\>]+\>.+?Мои бывшие.+?<div class="o-grid".+?(?P<cars>(\s+{cars})+)'
                # params
                .format(cars = recar)
            ), html)
            if (len(ucars)) == 0: raise Exception('ucars former are not found')
            ucars = ucars[0]
            for m in d2re(recar, ucars['cars'], False):
                ucar = d2re((
                    # img 
                    u'\<img src="(?P<img>[^"]+)'
                    # url & name
                    u'.+?\<a class="c-car-title[^\>]+href="(?P<url>[^"]+)"[^\>]*\>(?P<name>[^\<]+)'
                    # blog count
                    u'.+?\<span class="counter[^\>]+\>(?P<cblog>[^\<]+)'
                ), m)
                if (len(ucar)) == 0: raise Exception('ucar former details is not found')
                ucar = ucar[0]
                cars.append({
                    'name': ucar['name'],
                    'img': ucar['img'].replace("-480", "-80"),
                    'url': ucar['url'],
                    'cblog': ucar['cblog'],
                    'former': '1',
                })
        return cars
    def ucarformer(html):
        car = []
        if hasheader(u'Моя бывшая', html):
            ucar = d2re((
                # car
                u'\<h\d[^\>]+\>.+?Моя бывшая.+?<div class="o-grid".+?(?P<car>(\s+{car})+)'
                # params
                .format(car = recar)
            ), html)
            if (len(ucar)) == 0: raise Exception('ucar former are not found')
            ucar = ucar[0]
            for m in d2re(recar, ucar['car'], False):
                ucar = d2re((
                    # img 
                    u'\<img src="(?P<img>[^"]+)'
                    # url & name
                    u'.+?\<a class="c-car-title[^\>]+href="(?P<url>[^"]+)"[^\>]*\>(?P<name>[^\<]+)'
                    # blog count
                    u'.+?\<span class="counter[^\>]+\>(?P<cblog>[^\<]+)'
                ), m)
                if (len(ucar)) == 0: raise Exception('ucar former details is not found')
                ucar = ucar[0]
                car.append({
                    'name': ucar['name'],
                    'img': ucar['img'].replace("-480", "-80"),
                    'url': ucar['url'],
                    'cblog': ucar['cblog'],
                    'former': '1',
                })
        return car
    def ucmu(html):
        cmu = []
        if hasheader(u'Состоит в сообществ', html):
            ucmu = d2re((
                # cmu
                u'<h\d[^>]+>Состоит в сообществ[^<]+</h\d>.+?<ul class="c-side-nav">\s+(?P<cmu>(\s+<li[^>]+>.+?</li>)+)'
            ), html)
            if (len(ucmu)) == 0: raise Exception('ucmu are not found')
            ucmu = ucmu[0]
            for m in d2re('(\s+<li[^>]+>.+?</li>)', ucmu['cmu'], False):
                uc = d2re((
                    # url & name
                    u'<a.+?href="(?P<url>[^"]+)"[^>]*>(?P<name>[^<]+)'
                ), m)
                if (len(uc)) == 0: raise Exception('uc is not found')
                uc = uc[0]
                cmu.append({
                    'url': uc['url'],
                    'name': uc['name'],
                    'adm': '0',
                })
        return cmu
    def ucmuadm(html):
        cmuadm = []
        if hasheader(u'Администрирует сообществ', html):
            ucmuadm = d2re((
                # cmuadm
                u'<h\d[^>]+>Администрирует сообществ.</h\d>.+?<ul class="c-side-nav">\s+(?P<cmuadm>(\s+<li[^>]+>.+?</li>)+)'
            ), html)
            if (len(ucmuadm)) == 0: raise Exception('ucmu adm are not found')
            ucmuadm = ucmuadm[0]
            for m in d2re('(\s+<li[^>]+>.+?</li>)', ucmuadm['cmuadm'], False):
                ucadm = d2re((
                    # url & name
                    u'<a.+?href="(?P<url>[^"]+)"[^>]*>(?P<name>[^<]+)'
                ), m)
                if (len(ucadm)) == 0: raise Exception('uc amd is not found')
                ucadm = ucadm[0]
                cmuadm.append({
                    'url': ucadm['url'],
                    'name': ucadm['name'],
                    'adm': '1',
                })
        return cmuadm
    def uads(html):
        ads = []
        if hasheader(u'<a[^>]+>Объявлени', html):
            uads = d2re((
                # ads
                u'<h\d[^>]+><a[^>]+>Объявлени.</a></h\d>.+?<ul class="c-side-nav">\s+(?P<ads>(\s+<li[^>]+>.+?</li>)+)'
            ), html)
            if (len(uads)) == 0: raise Exception('uads are not found')
            uads = uads[0]
            for m in d2re('(\s+<li[^>]+>.+?</li>)', uads['ads'], False):
                uad = d2re((
                    # url & name
                    u'<a.+?href="(?P<url>[^"]+)"[^>]*>(?P<name>[^<]+)'
                ), m)
                if (len(uad)) == 0: raise Exception('uad is not found')
                uad = uad[0]
                ads.append({
                    'url': uad['url'],
                    'name': uad['name'],
                })
        return ads

    htmlpath = 'usrs.rzn.html'
    jsonpath = 'usrs.rzn.json'
    print 'removing directory {}'.format(d2dbhtmlpath(htmlpath))
    shutil.rmtree(d2dbhtmlpath(htmlpath))
    ufs = os.listdir(d2dbhtmlpath(htmlpath))
    uc = len(ufs)
    for i, usr in enumerate(ufs):
        print 'parsing {} from {}: {}'.format(i + 1, uc, usr)
        html = d2dbr('{}/{}'.format(htmlpath, usr))
        u = {}
        u.update(uinfo(usr, html))
        u.update({'cars': []})
        u['cars'].extend(ucar(html))
        u['cars'].extend(ucars(html))
        u['cars'].extend(ucarsformer(html))
        u.update({'communities': []})
        u['communities'].extend(ucmu(html))
        u['communities'].extend(ucmuadm(html))
        u.update({'ads': []})
        u['ads'].extend(uads(html))
        d2dbw(u'{}/{}'.format(jsonpath, usr), json.dumps(u, indent = 2, ensure_ascii = False))

d2usrsrzndetails()
