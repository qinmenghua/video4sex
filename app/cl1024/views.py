#-*- coding=utf-8 -*-
import datetime
from flask import jsonify, redirect, render_template, request, url_for, flash, session, jsonify, g
from flask_login import login_required, current_user
from . import cl
from .. import db
from ..models import *
from ..auth.forms import *
from ..main.forms import *


forums = {
    'a': '技术讨论区',
    'b': '新时代的我们',
    'c': '达盖尔的旗帜',
    'd': '成人文学',
    'e': 'HTTP下载区',
    'f': '在线成人影院',
    'g': '亚洲无码原创区',
    'h': '亚洲无码转载区',
    'i': '亚洲有码原创区',
    'j': '亚洲有码转载区',
    'k': '欧美原创区',
    'l': '欧美转载区',
    'm': '动漫原创区',
    'n': '动漫转载区'
}


# cl


@cl.route('/cl')
#@login_required
def clindex():
    forumid = request.args.get('forum', 'a')
    page = request.args.get('page', 1, type=int)
    if page == 0:
        page = 1
    if page > 10 and not current_user.is_authenticated:
        page = 10
        flash('需要注册才可查看更多内容！')
    forum = forums[forumid]
    pagination = clPost.query.filter_by(forum=forumid).order_by(
        clPost.id.desc()).paginate(page, per_page=20, error_out=False)
    posts = pagination.items
    return render_template('cl/index.html',
                           forum=forum,
                           forumid=forumid,
                           pagination=pagination,
                           posts=posts)


@cl.route('/post', methods=['POST', 'GET'])
#@login_required
def clpost():
    forumid = request.args.get('forum')
    id = int(request.args.get('id'))
    post = clPost.query.filter_by(id=id).first()
    form = CommentForm(request.form, follow=-1, vid=id)

    try:
        username = current_user.username
    except:
        username = 'ddddaxdesdd'
    return render_template('cl/content.html',
                           post=post,
                           forum=forumid,
                           user=username
                           )


@cl.route('/post', methods=['POST'])
@login_required
def delete():
    forumid = request.args.get('forum')
    id = int(request.args.get('id'))
    forum = forums[forumid]
    cursor.execute('delete from posts where id=' + str(id))
    return redirect(url_for('cl1024.clindex', forumid=forumid))
