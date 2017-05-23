#-*- coding=utf-8 -*-

from threading import Thread
import requests
import re
import os
import Queue
import time
import urllib2
from app import db
from app.models import clPost as Post
import sys
reload(sys)
sys.setdefaultencoding('utf8')

forums={
    '7':'a',
    '8':'b',
    '16':'c',
    '20':'d',
    '21':'e',
    '22':'f',
    '2':'g',
    '17':'h',
    '15':'i',
    '18':'j',
    '4':'k',
    '19':'l',
    '5':'m',
    '24':'n'
}


clurl='http://t66y.com/'
furl=clurl+'thread0806.php?fid=%s&search=&page='

post_reg=re.compile('href="(htm_data/\d{1,2}/\d{4}/\d{7}.html)"')
cont_reg=re.compile('<div class="tips" style="width:auto"><SCRIPT LANGUAGE="JavaScript">spinit\(\);</SCRIPT></div><div class="c"></div>([\w\W]*?)<span><a class="s3" title=".*?" style="cursor:pointer;" onclick="postreply\(\'.*?\',\'0\',\'tpc\'\);">.*?</a></span>')
title_reg=re.compile('<title>(.*?)  ')
time_reg=re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}')


class CL(Thread):
    def __init__(self,queue,out_queue):
        super(CL,self).__init__()
        self.queue=queue
        self.out=out_queue
    
    def run(self):
        while 1:
            url=self.queue.get()
            try:
                print 'start parse ',url
                cont=requests.get(url).content
                urls=post_reg.findall(cont)
                bb=list(set(urls))
                cc=sorted(bb,key=lambda x:int(x.split('/')[-1].split('.')[0]),reverse=True)
                for line in cc:
                    self.out.put(line)
            except Exception,e:
                print e


class Consumer(Thread):

    def __init__(self, queue):
        super(Consumer, self).__init__()
        self.queue = queue

    def run(self):
        session = requests.Session()
        while 1:
            if self.queue.empty():
                continue
            else:
                link = clurl+self.queue.get()
                print 'start parse post: ' + link
                try:
                    response = session.get(link)
                    response.encoding = 'gbk'
                    content=response.text
                    title=title_reg.findall(content)[0]
                    body=cont_reg.findall(content)[0]
                    time=time_reg.findall(body)[0]
                    c2=re.sub('input','img class="img-responsive center-block"',body)
                    c3=re.sub("type='image'",'',c2)
                    c4=re.sub(' onclick=".*?"','',c3)
                    c5=re.sub(" style='cursor:pointer'",'',c4)
                    id=int(link.split('/')[-1].split('.')[0])
                    forumid=forums[link.split('/')[4]]
                    print 'the type of title is ',type(title[0])
                    #print title[0]
                    #print body[0][:1000]
                    if not Post.query.filter_by(id=id).first():
                        d=Post(id,unicode(title).encode("utf-8"),unicode(c5).encode("utf-8"),forumid,time)
                        db.session.add(d)
                        db.session.commit()
                except Exception, e:
                    print e
                    print 'url: %s parse failed\n' % link
            if self.queue.empty():
                break
                
if __name__=='__main__':
    url_queue=Queue.Queue()
    out=Queue.Queue()
    try:
        max_page=int(sys.argv[1])
    except:
        max_page=1
    for key in forums.keys():
        url=furl%key
        urls=[url+str(d) for d in range(1,max_page+1)]
        for ul in urls:
            url_queue.put(ul)
    for i in range(4):
        task=CL(url_queue,out)
        task.start()
    for i in range(4):
        a=Consumer(out)
        a.start()

    
