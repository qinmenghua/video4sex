#-*- coding=utf-8 -*-
import requests
import re
from threading import Thread
import Queue
import urllib2
from app import db
from app.models import Post, onlineTag
import sys
import argparse
import datetime
from hashlib import md5
import logging


logger = logging.getLogger("fahai_crawler")
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler("/root/video4sex/logs/fahai.log")
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


fahai = 'http://www.yesok9.com'
fahai_url = fahai

flag = {fahai_url: 'fahai'}


def timenow():
    return datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')

proxies = {}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
           'Upgrade-Insecure-Requests': '1'}
parser = argparse.ArgumentParser()
parser.add_argument('-t', default='new')
parser.add_argument('-a1', default=1, type=int)
parser.add_argument('-a2', default=1, type=int)
args = parser.parse_args()

urls = {fahai_url: [args.a1, args.a2]}

url_reg = re.compile('<a href="(.*?)" title=".*?" class="thumb th">')
mp4_reg = re.compile(
    'div id="kt_player">[\w\W]*?<iframe src="(.*?)" frameborder="0" width="100%" height="100%" scrolling="no">')
title_reg = re.compile('<title>(.*?)-.*?</title>')
id_reg = re.compile(
    '<script language="javascript" type="text/javascript">getDigg\((.*?)\);</script>')
pic_reg = re.compile(
    '<img src="(http://.*?fahai\d+?\.club/\d+?/\w+?//2.jpg)" alt=".*?" height="\d+?" width="\d+?">')
tag_reg = re.compile(
    '''<div class="wrap_cell">[\w\W]*?<a href='(.*?)'>(.*?)</a>''')


url_queue = Queue.Queue()
url2_queue = Queue.Queue()
for url in urls.keys():
    posts_url = url + '/av/All/page_51_%d.html'
    for i in range(urls[url][0], urls[url][1] + 1):
        page_url = posts_url % i
        url_queue.put([url, page_url])


class Get(Thread):
    def __init__(self, queue):
        super(Get, self).__init__()
        self.queue = queue

    def run(self):
        while 1:
            url = self.queue.get()
            logger.info('start parse ' + url[1])
            try:
                headers['Upgrade-Insecure-Requests'] = url[1].split('/')[-1]
                resp = requests.get(url[1], headers=headers, proxies=proxies)
                cont = resp.content
                urls = url_reg.findall(cont)
                for ul in urls:
                    id = ul.split('/')[-1].split('.')[0]
                    if Post.query.filter_by(flag='fahai', id=id).count() == 0:
                        url2_queue.put([url[0], url[0] + ul])
            except Exception, e:
                logger.info(e)
            if self.queue.empty():
                break


class Get2(Thread):
    def __init__(self, queue):
        super(Get2, self).__init__()
        self.queue = queue

    def run(self):
        while 1:
            url = self.queue.get()
            logger.info('start parse ' + url[1])
            try:
                resp = requests.get(url[1])
                cont = resp.content
                title = title_reg.findall(cont)[0]
                pic = pic_reg.findall(cont)[0]
                pic = pic.split('/', 3)[-1]
                mp4 = mp4_reg.findall(cont)[0]
                id = url[1].split('/')[-1].split('.')[0]
                # c=urllib2.urlopen(mp4)
                mp44 = mp4
                mp4 = mp4.split('/', 3)[-1]
                en = 'fahai' + '#' + id
                m1 = md5(en)
                encode = m1.hexdigest()
                f = flag[url[0]]
                try:
                    data = Post(zhan='http://sp1.fahai51.club', flag='fahai', id=id, title=title, picture=pic,
                                video=mp44, raw_video=mp4, encode=encode, createtime=timenow())
                    db.session.add(data)
                    db.session.commit()
                    tags = tag_reg.findall(cont)
                    if len(tags) > 0:
                        for tag in tags:
                            logger.info(tag)
                            tagdata = onlineTag(tag=tag[1], url=tag[
                                                0], encode_id=encode)
                            db.session.add(tagdata)
                        db.session.commit()
                    logger.info(id + ' insert successfully')
                except Exception, e:
                    logger.info(e)
                    logger.info(str(id) + ' : insert fail')
            except Exception, e:
                logger.info(e)
            if self.queue.empty():
                break

if args.t == 'reload':
    try:
        fin = open('out.txt', 'r').readlines()
        fin2 = open('done.txt', 'r').readlines()
        nodone = list(set(fin) ^ set(fin2))
        for line in nodone:
            url2_queue.put([url[0], url[0] + ul])
        for i in range(5):
            t1 = Get2(url2_queue)
            t1.start()
    except:
        for i in range(2):
            t = Get(url_queue)
            t.start()
        for i in range(5):
            t1 = Get2(url2_queue)
            t1.start()
else:
    for i in range(2):
        t = Get(url_queue)
        t.start()
    for i in range(5):
        t1 = Get2(url2_queue)
        t1.start()
