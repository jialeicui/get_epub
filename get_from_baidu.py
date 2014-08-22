#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import gzip
import cStringIO
import re
import HTMLParser
import sys
import cookielib

cookie=cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Mobile/9B176 MicroMessenger/4.3.2'
opener.addheaders = [('User-agent', user_agent)]

def open_url(url):
    try:
        resp=opener.open(url, None)

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

def get_bookurl(bookname):
    url = 'http://m.baidu.com/s?word=%s&tn=iphone' %(bookname)
    query = open_url(url)
    res = re.search('<div class="box-card">(.*?)</div>', query).group(1)
    url = re.search('<a href="(.*?)"', res).group(1)
    url = HTMLParser.HTMLParser().unescape(url)

    return get_real_url(url)
    pass

def get_chapter_info(bookname):
    url = get_bookurl(bookname)
    content = open_url(url)
    print content
    res = re.findall('', content, re.U)
    return res
    pass

def get_chapter(url):
    content = open_url(url).decode('gbk')
    res = re.search('<div class="content">(.*?)</div>\s+<div align="center"><script language="javascript"', content, re.S)
    if res:
        c = res.group(1).replace('<br />','')
        c = re.sub('<a href=\'.*\'>','', c, re.S)
        c = re.sub('</a>','', c, re.S)
        return HTMLParser.HTMLParser().unescape(c)
    pass

def get_book(bookname):
    chapters = get_chapter_info(bookname)
    print chapters
    sys.exit(0)
    chapters = chapters[3:]
    for url,name in chapters:
        c = get_chapter(url)

        return
    pass

if __name__ == '__main__':
    get_book('大主宰')



