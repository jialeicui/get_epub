#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys

import json
import urllib
import urllib2
import urlparse
import cookielib
import HTMLParser

import shutil
import gzip
import zipfile

import cStringIO

reload(sys)
sys.setdefaultencoding('utf-8')

class GetEpub(object):
    """get books from m.baidu.com and make epub"""
    def __init__(self):
        self.cookie=cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Mobile/9B176 MicroMessenger/4.3.2'
        self.opener.addheaders = [('User-agent', user_agent)]

    def __open_url(self, url, data = None):
        if data:
            url = url + urllib.urlencode(data)
        try:
            resp=self.opener.open(url)

            # status code 200 - 'ok'.
            if resp.code==200:
                html = resp.read()
                # 处理可能存在的压缩
                if html[:6] == '\x1f\x8b\x08\x00\x00\x00':
                    html = gzip.GzipFile(fileobj = cStringIO.StringIO(html)).read()
                return html
            else:
                return None
        except Exception, e:
            print e
            return None 

    def __get_real_url(self, url):
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

    def get_book_info(self, bookname):
        url = 'http://m.baidu.com/s?word=%s&tn=iphone' %(bookname)
        query = self.__open_url(url)
        res = re.search('<div class="box-card">(.*?)</div>', query).group(1)
        url = re.search('<a href="(.*?)"', res).group(1)
        url = HTMLParser.HTMLParser().unescape(url)

        baidu_url = self.__get_real_url(url)
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
            'hasRp':'true'
        }
        content = self.__open_url('http://m.baidu.com/tc?', data)
        return json.loads(content)['data']
        pass

    def get_book_json(self, src, gid, cid):
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

        query = self.__open_url('http://m.baidu.com/tc?', data)
        res = json.loads(query)['data']
        content = res['content']
        # content = content.replace('<p style="text-indent:2em;">','    ')
        # content = content.replace('</p>','\n')
        return content
        pass

    def __create_content(self, index, title, content):
        temp_con=open('content.html', 'r').read()
        temp_con = temp_con.replace("{{title}}",title).replace("{{content}}",content)
        open(index+'.html','w').write(temp_con)
        pass

    def __create_catalog_and_book(self, book_info):
        item_template     = '<item id="%s" href="%s.html" media-type="application/xhtml+xml" />'
        itemref_template  = '<itemref idref="%s" />'
        navPoint_template = '<navPoint id="%s" playOrder="%s"><navLabel><text>%s</text></navLabel><content src="%s.html"/></navPoint>'
        title_template    = '<li><a href="%s.html">%s</a></li>'

        itemlist     = []
        itemreflist  = []
        navPointlist = []
        titlelist    = []

        for c in book_info['group']:
            contentid = c['index']
            title     = c['text']

            itemlist.append(item_template % (contentid, contentid))
            itemreflist.append(itemref_template % contentid)
            navPointlist.append(navPoint_template % (contentid, contentid, title, contentid))
            titlelist.append(title_template % (contentid, title))

        def get_fill_info():
            ret_info = {}
            ret_info['subject']     = book_info['category']
            ret_info['bookname']    = book_info['title']
            ret_info['author']      = book_info['author']
            ret_info['description'] = book_info['summary']
            ret_info['bookid']      = 'C%s' % book_info['last_chapter_cid'].split('|')[0]
            ret_info['rights']      = 'Copyright (C) XXX'

            ret_info['itemlist']     = ''.join(itemlist)
            ret_info['itemreflist']  = ''.join(itemreflist)
            ret_info['navPointlist'] = ''.join(navPointlist)
            ret_info['titlelist']    = ''.join(titlelist)
            return ret_info
            pass

        def fill_info(filename):
            f = open(filename, 'r+')
            content = f.read()
            f.seek(0)
            f.truncate()
            # hold %
            content = content.replace('%','%%')
            content=re.sub('(\{\{[a-z]{1,20}\}\})',lambda x:"".join(['%','(',x.group(1)[2:-2],')','s']) , content, re.U)
            content = content % get_fill_info()
            # rollback %
            content = content.replace('%%','%')

            f.write(content)
            pass

        fill_info('catalog.html')
        fill_info('toc.ncx')
        fill_info('content.opf')
        fill_info('title.xhtml')

        # cover
        # get cover.jpg 
        jpg=file('cover.jpg','wb')
        jpg.write(self.__open_url(book_info['coverImage']))
        jpg.close()

        # create
        epub_path='../%s.epub' % book_info['title']
        if os.path.exists(epub_path):
            os.remove(epub_path)
        zip=zipfile.ZipFile(epub_path,'w',zipfile.ZIP_DEFLATED)
        for b,ds,fs in os.walk('.'):
            for ff in fs:
                zip.write(os.path.join(b,ff))
        zip.close()
        pass

    def get_book(self, bookname):
        book_info = self.get_book_info(bookname)
        gid = book_info['gid']
        chapters = book_info['group']

        if os.path.exists(bookname):
            shutil.rmtree(bookname)
        shutil.copytree('epub_template',bookname)
        os.chdir(bookname)

        for c in chapters:
            print c['text']
            content = self.get_book_json(c['href'], gid, c['cid'])
            self.__create_content(c['index'], c['text'], content)
            break
        self.__create_catalog_and_book(book_info)

        #clean
        os.chdir('../')
        shutil.rmtree(bookname)
        pass

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(u'python main.py 小说名')
        pass
    epub = GetEpub()
    epub.get_book(sys.argv[1])
