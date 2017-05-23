#-*- coding=utf-8 -*-
import datetime
from flask import jsonify, redirect, render_template, request, url_for, flash, session, jsonify, g
from flask_login import login_required, current_user
from . import online
from .. import db
from ..models import *
from ..auth.forms import *
import random
import re
import requests
import urllib2
from .. import logger
from ..main.forms import CommentForm
import time

headers = {
    'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def test(url):
    """
    req = urllib2.Request(url)
    req.add_header(
        'User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    r = urllib2.urlopen(req)
    """
    if int(url.split('/')[7]) > time.time():
        r = 'ok'
    else:
        r = 'fail'
    return r


def update_url(flag, id):
    mp4_url = Post.query.filter_by(flag=flag, id=id).first()
    mp4url = mp4_url.zhan + '/' + str(mp4_url.id)
    logger.info('the web :' + mp4url)
    try:
        cont = requests.get(mp4url, headers=headers).content
        mp4 = mp4_reg.findall(cont)
        mp4 = mp4[0]
        mp4_url.video = mp4
        db.session.add(mp4_url)
        db.session.commit()
        logger.info(flag + id + ' update success')
    except Exception, e:
        logger.info(e)


@online.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
    global ip
    try:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    except:
        ip = request.remote_addr


# online

@online.route('/ajax', methods=['POST'])
@login_required
def ajax():
    zhan = request.form.get('zhan')
    vid = request.form.get('vid')
    rating = request.form.get('rating', type=int)
    print 'rating:', rating
    c = Post.query.filter_by(zhan=zhan, id=vid).first()
    if rating == 1:
        c.ilike += 1
    elif rating == -1:
        c.unlike += 1
    db.session.add(c)
    db.session.commit()
    c = Post.query.filter_by(zhan=zhan, id=vid).first()
    return jsonify(dict(like=c.ilike, unlike=c.unlike))


@online.route('/online')
#@login_required
def index():
    page = request.args.get('page', 1, type=int)
    sortby = request.args.get('sortby', 'id')
    rever = request.args.get('rever', 'desc')
    """
    if page > 2 and not current_user.is_authenticated:
        page = 1
        flash('需要注册才可查看更多内容！')
    """
    if sortby == 'id' and rever == 'asc':
        pagination = Post.query.filter_by(isvalid=1, isvip=False).order_by(
            Post.createtime.asc()).paginate(page, per_page=20, error_out=False)
    elif sortby == 'id' and rever == 'desc':
        pagination = Post.query.filter_by(isvalid=1, isvip=False).order_by(
            Post.createtime.desc()).paginate(page, per_page=20, error_out=False)
    elif sortby == 'hot' and rever == 'desc':
        pagination = Post.query.filter_by(isvalid=1, isvip=False).order_by(
            Post.viewtimes.desc()).paginate(page, per_page=20, error_out=False)
    elif sortby == 'hot' and rever == 'asc':
        pagination = Post.query.filter_by(isvalid=1, isvip=False).order_by(
            Post.viewtimes.asc()).paginate(page, per_page=20, error_out=False)
    else:
        pagination = Post.query.filter_by(isvalid=1, isvip=False).order_by(
            Post.createtime.desc()).paginate(page, per_page=20, error_out=False)
    sql = 'select a.tag from onlinetags a join (select tag,count(1) from onlinetags group by tag having count(1)>=10) b on a.tag=b.tag group by tag;'
    result = db.session.execute(sql)
    tags = result.fetchall()
    posts = pagination.items
    return render_template('online/index.html', posts=posts, pagination=pagination, sortby=sortby, rever=rever, tags=tags, endpoint='online.index', vip='')


@online.route('/tags')
def tagindex():
    tag = request.args.get('tag')
    page = request.args.get('page', 1, type=int)
    sortby = request.args.get('sortby', 'id')
    rever = request.args.get('rever', 'desc')
    if page > 2 and not current_user.is_authenticated:
        page = 1
        flash('需要注册才可查看更多内容！')
        pagination = onlineTag.query.filter_by(
            tag=tag).paginate(page, per_page=20, error_out=False)
    else:
        pagination = onlineTag.query.filter_by(
            tag=tag).paginate(page, per_page=20, error_out=False)
    sql = 'select a.tag from onlinetags a join (select tag,count(1) from onlinetags group by tag having count(1)>=10) b on a.tag=b.tag group by tag;'
    result = db.session.execute(sql)
    tags = result.fetchall()
    posts = pagination.items
    return render_template('online/tag_index.html', posts=posts, pagination=pagination, sortby=sortby, rever=rever, tags=tags, tag=tag)


@online.route('/online/vip')
@login_required
def vip_index():
    page = request.args.get('page', 1, type=int)
    sortby = request.args.get('sortby', 'id')
    rever = request.args.get('rever', 'desc')
    if page > 2 and not current_user.isvip:
        page = 1
        flash('先锋计划才可观看更多内容')
    if sortby == 'id' and rever == 'asc':
        pagination = Post.query.filter_by(isvalid=1, isvip=True).order_by(
            Post.createtime.asc()).paginate(page, per_page=20, error_out=False)
    elif sortby == 'id' and rever == 'desc':
        pagination = Post.query.filter_by(isvalid=1, isvip=True).order_by(
            Post.createtime.desc()).paginate(page, per_page=20, error_out=False)
    elif sortby == 'hot' and rever == 'desc':
        pagination = Post.query.filter_by(isvalid=1, isvip=True).order_by(
            Post.viewtimes.desc()).paginate(page, per_page=20, error_out=False)
    elif sortby == 'hot' and rever == 'asc':
        pagination = Post.query.filter_by(isvalid=1, isvip=True).order_by(
            Post.viewtimes.asc()).paginate(page, per_page=20, error_out=False)
    else:
        pagination = Post.query.filter_by(isvalid=1, isvip=True).order_by(
            Post.createtime.desc()).paginate(page, per_page=20, error_out=False)
    sql = 'select a.tag from onlinetags a join (select tag,count(1) from onlinetags group by tag having count(1)>=10) b on a.tag=b.tag group by tag;'
    result = db.session.execute(sql)
    tags = result.fetchall()
    posts = pagination.items
    return render_template('online/index.html', posts=posts, pagination=pagination, sortby=sortby, rever=rever, tags=tags, endpoint='online.vip_index', vip='/vip')


@online.route('/online/play', methods=['GET', 'POST'])
def playon():
    isrand = request.args.get('random', '0')
    vid = request.args.get('vid')
    mp4_url = Post.query.filter_by(encode=vid).first()
    if mp4_url is None:
        flash('视频不存在或者链接已失效')
        return redirect(url_for('online.index'))
    logger.info('try to fetch %(flag)s %(id)s' %
                {'flag': mp4_url.flag, 'id': mp4_url.id})
    form = CommentForm(request.form, follow=-1, vid=vid)
    comments = mp4_url.comments.order_by(Comment.timestamp.asc()).all()
    if current_user.is_authenticated:
        userid = current_user.id
        encode_id = vid
        ViewHistory.add_view(userid, encode_id)
    time = datetime.datetime.now()
    # ip=request.headers['X-Forwarded-For'].split(',')[0]
    date = int(time.strftime('%Y%m%d'))
    i = IP.query.filter_by(ip=ip, date=date).first()
    if i is not None:
        count = i.count
    else:
        count = 0
    if isrand == 'random':
        IP.add_count(db, ip, date)
    rand = Post.query.filter_by(isvalid=1, isvip=False).all()
    rand = random.choice(rand)
    info = '明天'
    Post.add_times(db, vid)
    mp4_reg = re.compile(
        '<source src="(.*?)" type="video/mp4" label="360p" res="360"')
    if mp4_url.flag in ('fahai', 'hdr'):
        mp4_url = mp4_url
    elif mp4_url.openload_url is not None and mp4_url.openload_expired < datetime.datetime.now():
        mp4_url = mp4_url
        mp4_url.openload_expired = datetime.datetime.now() + datetime.timedelta(days=60)
        db.session.add(mp4_url)
        db.session.commit()
    else:
        logger.info('checking ' + mp4_url.flag + ' ' + mp4_url.id)
        if test(mp4_url.video) == 'ok':
            mp4_url = Post.query.filter_by(encode=vid).first()
            logger.info(str(mp4_url.flag) + ' ' + str(mp4_url.id) + ' is ok~')
        else:
            mp4_url = Post.query.filter_by(encode=vid).first()
            logger.info(str(mp4_url.flag) + ' ' +
                        str(mp4_url.id) + ' is fail !')
            mp4url = mp4_url.zhan + '/' + str(mp4_url.id)
            logger.info('the web :' + mp4url)
            try:
                cont = requests.get(mp4url, headers=headers).content
                mp4 = mp4_reg.findall(cont)
                mp4 = mp4[0]
                mp4_url.video = mp4
                db.session.add(mp4_url)
                db.session.commit()
                mp4_url = Post.query.filter_by(encode=vid).first()
            except Exception, e:
                logger.info(e)
                flash("无法打开")
                return redirect(url_for('online.index'))
    return render_template('online/play.html', url=mp4_url, rand=rand, info=info, count=count, vid=vid, form=form, comments=comments)


@online.route('/online/bigdata')
def bigdata():
    return render_template('online/bigdata.html')
