#-*- coding=utf-8 -*-
from .. import db
from ..models import *
from ..auth.forms import LoginForm, RegistrationForm
from flask import render_template, redirect, request, url_for, flash, session, jsonify, g
from flask_login import login_user, logout_user, login_required, \
    current_user
from ..email import send_email
from ..decorators import admin_required, permission_required
from . import main
from .forms import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import time
import subprocess
import requests
import re
import datetime
import pytz
from random import choice, randint
import urllib2
import datetime
import json
import random


tz = pytz.timezone('Asia/Shanghai')


@main.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
    global ip
    try:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    except:
        ip = request.remote_addr


@main.route('/', methods=['GET', 'POST'])
def home():
    return redirect(url_for('online.index'))

# other


@main.route('/search')
def search():
    try:
        keyword = request.args.get('q')
    except:
        keyword = 'sddddsfdfdfdddsasf'
    clposts = clPost.query.filter(clPost.title.ilike('%%%s%%' % keyword)).all()
    onlineposts = Post.query.filter_by(isvalid=1, isvip=False).filter(
        Post.title.ilike('%%%s%%' % keyword)).all()
    return render_template('search.html', keyword=keyword, clposts=clposts, onlineposts=onlineposts)


# comment
@main.route('/comment', methods=["POST"])
@login_required
def comment():
    form = CommentForm()
    referer = request.headers['Referer']
    if form.validate_on_submit():
        comment = Comment(article_id=form.vid.data,
                          content=form.content.data,
                          author_name=form.name.data,
                          author_email=form.email.data)
        db.session.add(comment)
        db.session.commit()
        followed_id = int(form.follow.data)
        if followed_id != -1:
            followed = Comment.query.get_or_404(followed_id)
            f = Follow(follower=comment, followed=followed)
            comment.comment_type = 'reply'
            comment.reply_to = followed.author_name
            db.session.add(f)
            db.session.add(comment)
            db.session.commit()
        flash(u'提交评论成功！')
        return redirect(referer)
    if form.errors:
        flash(u'发表评论失败')
        return redirect(referer)


@main.route('/manage-comments/disable/<int:id>')
@login_required
@admin_required
def disable_comment(id):
    referer = request.headers['Referer']
    comment = Comment.query.get_or_404(id)
    vid = comment.post.encode
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    flash(u'屏蔽评论成功！', 'success')
    if request.args.get('disable_type') == 'admin':
        page = request.args.get('page', 1, type=int)
        return redirect(url_for('main.manage_comments',
                                page=page))

    return redirect(referer)


@main.route('/manage-comments/enable/<int:id>')
@login_required
@admin_required
def enable_comment(id):
    referer = request.headers['Referer']
    comment = Comment.query.get_or_404(id)
    vid = comment.post.encode
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    flash(u'恢复显示评论成功！', 'success')
    if request.args.get('enable_type') == 'admin':
        page = request.args.get('page', 1, type=int)
        return redirect(url_for('main.manage_comments',
                                page=page))

    return redirect(referer)


# 单条评论的删除，这里就不使用表单或者Ajax了，这与博文的管理不同，但后面多条评论的删除会使用Ajax
# 前面在admin页面删除单篇博文时使用表单而不是Ajax，其实使用Ajax效果会更好，当然这里只是尽可能
# 使用不同的技术，因为以后在做自动化运维开发时总有用得上的地方
@main.route('/manage-comments/delete-comment/<int:id>')
@login_required
@admin_required
def delete_comment(id):
    referer = request.headers['Referer']
    comment = Comment.query.get_or_404(id)
    vid = comment.post.encode
    article_id = comment.article_id
    db.session.delete(comment)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash(u'删除评论失败！', 'danger')
    else:
        flash(u'删除评论成功！', 'success')
    if request.args.get('delete_type') == 'admin':
        page = request.args.get('page', 1, type=int)
        return redirect(url_for('main.manage_comments',
                                page=page))

    return redirect(referer)


@main.route('/manage-comments', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_comments():
    form = AdminCommentForm(follow=-1, article=-1)
    form2 = DeleteCommentsForm(commentIds=-1)

    if form.validate_on_submit():
        article = Article.query.get_or_404(int(form.article.data))
        comment = Comment(article_id=form.vid.data,
                          content=form.content.data,
                          author_name=form.name.data,
                          author_email=form.email.data)
        db.session.add(comment)
        db.session.commit()

        followed = Comment.query.get_or_404(int(form.follow.data))
        f = Follow(follower=comment, followed=followed)
        comment.comment_type = 'reply'
        comment.reply_to = followed.author_name
        db.session.add(f)
        db.session.add(comment)
        db.session.commit()
        flash(u'提交评论成功！', 'success')
        return redirect(url_for('.manage_comments'))
    if form.errors:
        flash(u'提交评论失败！请查看填写有无错误。', 'danger')
        return redirect(url_for('.manage_comments'))

    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('admin/manage_comments.html', User=User,
                           Comment=Comment, comments=comments,
                           pagination=pagination, page=page,
                           endpoint='.manage_comments', form=form, form2=form2)


@main.route('/manage-comments/delete-comments', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_comments():
    form2 = DeleteCommentsForm(commentIds=-1)

    if form2.validate_on_submit():
        commentIds = json.loads(form2.commentIds.data)
        count = 0
        for commentId in commentIds:
            comment = Comment.query.get_or_404(int(commentId))
            count += 1
            db.session.delete(comment)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'删除失败！', 'danger')
        else:
            flash(u'成功删除%s条评论！' % count, 'success')
    if form2.errors:
        flash(u'删除失败！', 'danger')

    page = request.args.get('page', 1, type=int)
    return redirect(url_for('.manage_comments', page=page))
