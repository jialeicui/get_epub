#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen, Request
import gzip
import cStringIO
import re
import HTMLParser
import sys

def open_url(url):
    req=Request(url)
    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Mobile/9B176 MicroMessenger/4.3.2'
    req.add_header('User-agent', user_agent)

    try:
        resp=urlopen(req,None,60)
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
    conn.request("HEAD", '/from=0/bd_page_type=1/ssid=0/uid=0/pu=usm%400%2Csz%40224_220%2Cta%40iphone___3_537/baiduid=DBF544B46BB2ECE56F3B647B45AA9BFC/w=0_10_%E5%A4%A7%E4%B8%BB%E5%AE%B0/t=iphone/l=1/tc?ref=www_iphone&lid=12283152388180642766&order=1&fm=alnv_book&tj=wise_novel_book_1_0_10_l1&sec=40826&di=406d01392c50e6f3&bdenc=1&nsrc=IlPT2AEptyoA_yixCFOxXnANedT62v3IGtiTNCVUB8SxokDyqRLrIxEtRD0fQGqPZpLRxWq4aNwYwn0wRjIz7aZ1t_Nkq7Eh9nvcgPruw2PKCBVdfhZmPMHUS7VrtOTam3cvdt2yF1EzAGcR8rS6t3stfQD3atBcndHSriymqfa02lmzD93ZnFrkZFw4HyGsDdjDaMylrm9dHZa_')
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

    print get_real_url(url)
    sys.exit(0)
    # return get_real_url(res)
    pass

def get_chapter_info(bookname):
    url = get_bookurl(bookname)
    content = open_url(url)
    res = re.findall('<dd><a href="(.*)"(.*)</a></dd>', content, re.U)
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
    chapters = chapters[3:]
    for url,name in chapters:
        c = get_chapter(url)
        open('cc.txt', 'w').write(c)
        return
    pass

if __name__ == '__main__':
    get_book('大主宰')



