#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import gzip
import cStringIO
import re
import HTMLParser
import sys
import cookielib
import urlparse
import json

reload(sys)
sys.setdefaultencoding('utf-8') 

cookie=cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Mobile/9B176 MicroMessenger/4.3.2'
opener.addheaders = [('User-agent', user_agent)]

def open_url(url, data = None):
    if data:
        url = url + urllib.urlencode(data)
        # sys.exit(0)
    try:
        resp=opener.open(url)

        # status code 200 - 'ok'.
        if resp.code==200:
            html = resp.read()
            if html[:6] == '\x1f\x8b\x08\x00\x00\x00':
                html = gzip.GzipFile(fileobj = cStringIO.StringIO(html)).read()
            return html
        else:
            return None
    except Exception, e:
        print e
        return None
    

def get_real_url(url):
    import httplib
    conn = httplib.HTTPConnection("m.baidu.com")
    url = url[len('http://m.baidu.com'):]
    conn.request("GET", url)
    res = conn.getresponse()
    res = res.getheaders()

    iskey = 0
    for r in res:
        for k in r:
            if iskey:
                return k
                pass
            if k == 'location':
                iskey = 1
                pass

def get_book_info(bookname):
    url = 'http://m.baidu.com/s?word=%s&tn=iphone' %(bookname)
    query = open_url(url)
    res = re.search('<div class="box-card">(.*?)</div>', query).group(1)
    url = re.search('<a href="(.*?)"', res).group(1)
    url = HTMLParser.HTMLParser().unescape(url)

    baidu_url = get_real_url(url)
    result = urlparse.urlparse(baidu_url)
    param = urlparse.parse_qs(result.query,True) 

    book_src = param['src'][0]
    gid      = param['gid'][0]
    baiduid  = param['baiduid'][0]

    data = {
        'srd':1,
        'appui':'alaxs',
        'ajax':1,
        'alalog':1,
        'gid':gid,
        'pageType':'router',
        'src':book_src,
        'dir':1,
        'ssid':0,
        'from':0,
        'uid':0,
        'pu':'usm@0,sz@1320_2001,ta@iphone_1_5.1_3_534',
        'bd_page_type':1,
        'baiduid':baiduid,
        'tj':'wise_novel_book_1_0_10_title',
        'id':'wisenovel',
        # 'logid':1409129041601296
        'hasRp':'true'
    }
    content = open_url('http://m.baidu.com/tc?', data)
    # return content
    return json.loads(content)['data']
    pass

def get_book_json(src, gid, cid):
    data = {
        'srd':1,
        'appui':'alaxs',
        'ajax':1,
        'gid':gid,
        'alals':1,
        'src':src,
        'cid':cid,
        'chapterIndex':1,
        'id':'wisenovel'
    };

    query = open_url('http://m.baidu.com/tc?', data)
    res = json.loads(query)['data']
    content = res['content']
    # content = content.replace('<p style="text-indent:2em;">','    ')
    # content = content.replace('</p>','\n')
    return content
    pass

def create_content(index, title, content):
    temp_con=open('epub_template/content.html', 'r').read()
    temp_con = temp_con.replace("{{title}}",title).replace("{{content}}",content)
    open(index+'.html','w').write(temp_con)
    pass

def create_catalog(book_info):
    catalog={
        'itemlist':['<item id="%(contentid)s" href="%(contentid)s.html" media-type="application/xhtml+xml" />',],
        'itemreflist':['<itemref idref="%(contentid)s" />',],
        'navPointlist':['<navPoint id="%(contentid)s" playOrder="%(no)s"><navLabel><text>%(title)s</text></navLabel><content src="%(contentid)s.html"/></navPoint>',],
        'titlelist':['<li%(even_class_flag)s><a href="%(contentid)s.html">%(title)s</a></li>']
    }
    for c in book_info['group']:
        
        pass

    pass
def get_book(bookname):
    book_info = get_book_info(bookname)
    gid = book_info['gid']
    chapters = book_info['group']
    for c in chapters:
        print c['text']
        content = get_book_json(c['href'], gid, c['cid'])
        create_content(c['index'], c['text'], content)
        sys.exit(0)

    pass

if __name__ == '__main__':
    get_book('大主宰')



