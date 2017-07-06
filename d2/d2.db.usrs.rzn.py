#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re, json, operator, datetime, shutil
from d2lib import d2re
from d2lib import d2jdump
from d2lib import d2html
from d2lib import d2ajax
from d2lib import d2dbr
from d2lib import d2dbw
from d2lib import d2dbpath

def d2cars():
    print "getting car list"
    jcars = d2re("\<a[^\>]+href=\"/r/(?P<car>[^\"/]+)/?\"[^\>]*>(?P<name>[^\<]+)", d2html("https://www.drive2.ru/cars"))
    for crow in jcars:
        print 'getting model list: "{}"'.format(crow["car"])
        jmodels = d2re("\<a[^\>]+class=\"c-link\"[^\>]+href=\"/r/{}/(?P<model>[^\"/]+)/?\"[^\>]*>(?P<name>[^\<]+)".format(crow["car"]), d2html("https://www.drive2.ru/r/{}".format(crow["car"])))
        if len(jmodels) > 0:
            print ' - models count: {}'.format(len(jmodels))
            crow["models"] = jmodels
            for mrow in jmodels:
                print 'getting generation list: "{}"'.format(mrow["name"])
                jgens = d2re("\<a[^\>]+class=\"c-link\"[^\>]+href=\"/r/{}/(?P<generation>g[^\"/]+)/?\"[^\>]*>(?P<name>[^\<]+)".format(crow["car"]), d2html("https://www.drive2.ru/r/{}/{}".format(crow["car"], mrow["model"])))
                if len(jgens) > 0:
                    print ' - generations count: {}'.format(len(jgens))
                    mrow["generations"] = jgens
    print "writing cars file"
    d2dbw('cars', d2jdump(jcars))

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
    print "getting rzn id"
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
    print " - rzn id: {}".format(rznid)
    print "reading cars db"
    jcars = json.loads(d2dbr('cars'))
    print "getting rzn car users"
    # debug
    #jcars = [{"car":"lada","name":u"Лада","models":[{"model":"m1506","name":"4x4 3D"}]}]
    # debug
    usrs = []
    for car in jcars:
        if "models" in car:
            for model in car["models"]:
                if "generations" in model:
                    for generation in model["generations"]:
                        print u' - reading generation html: [{}] {} - {}'.format(car["name"], model["name"], generation["name"])
                        html = d2carhtml("https://www.drive2.ru/r/{}/{}/?city={}".format(car["car"], generation["generation"], rznid), rznid)
                        for u in d2re("/users/(?P<usr>[^/\?\"\'\<]+)", html):
                            if u["usr"] not in usrs:
                                usrs.append(u["usr"])
                else:
                    print u' - reading model html: [{}] {}'.format(car["name"], model["name"])
                    html = d2carhtml("https://www.drive2.ru/r/{}/{}/?city={}".format(car["car"], model["model"], rznid), rznid)
                    for u in d2re("/users/(?P<usr>[^/\?\"\'\<]+)", html):
                        if u["usr"] not in usrs:
                            usrs.append(u["usr"])
        else:
            print u' - reading car html: [{}]'.format(car["name"])
            html = d2carhtml("https://www.drive2.ru/r/{}/?city={}".format(car["car"], rznid), rznid)
            for u in d2re("/users/(?P<usr>[^/\?\"\'\<]+)", html):
                if u["usr"] not in usrs:
                    usrs.append(u["usr"])
    print 
    print "count: {}".format(len(usrs))
    print "writing rzn users file"
    d2dbw('usrs.rzn', "\n".join(usrs))
    
def d2usrsrznhtml():
    htmlpath = 'usrs.rzn.html'
    hfpath = d2dbpath(htmlpath)
    if os.path.isdir(hfpath) and os.path.exists(hfpath):
        print 'removing directory {}'.format(hfpath)
        shutil.rmtree(hfpath)
    usrs = d2dbr('usrs.rzn').splitlines()
    uc = len(usrs)
    for i, usr in enumerate(usrs):
        print 'downloading html {} from {}: {}'.format(i + 1, uc, usr)
        d2dbw(u'/{}'.format(usr), unicode(d2html(u'https://www.drive2.ru/users/{}'.format(usr)), 'utf-8'))
    
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
    jfpath = d2dbpath(jsonpath)
    if os.path.isdir(jfpath) and os.path.exists(jfpath):
        print 'removing directory {}'.format(jfpath)
        shutil.rmtree(jfpath)
    ufs = os.listdir(d2dbpath(htmlpath))
    uc = len(ufs)
    for i, usr in enumerate(ufs):
        print 'parsing html {} from {}: {}'.format(i + 1, uc, usr)
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

# 1. getting cars list
d2cars()

# 2. getting d2 rzn users
d2usrsrzn()

# 3. getting d2 rzn users html
d2usrsrznhtml()

# 4. getting d2 rzn users json
d2usrsrzndetails()
