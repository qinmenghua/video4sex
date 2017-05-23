#-*- coding=utf-8 -*-
from app import app, db, admin
from app.models import *
from auth.forms import *
from flask import render_template, redirect, request, url_for, flash, session, jsonify, g, current_app
from flask_login import login_user, logout_user, login_required, \
    current_user
from app.email import send_email
from app.decorators import admin_required, permission_required
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
    global ip
    try:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    except:
        ip = request.remote_addr


@app.context_processor
def form_trans():
    global ip
    try:
        username = current_user.username
    except:
        username = 'ddddaxdesdd'
    return dict(Permission=Permission, loginform=LoginForm(), regform=RegistrationForm())


class UserView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False
    # 这三个变量定义管理员是否可以增删改，默认为True
    can_delete = True
    can_edit = True
    can_create = True

    # 这里是为了自定义显示的column名字
    column_labels = dict(
        username=u'用户名',
        last_seen=u'最近登录',
    )

    # 如果不想显示某些字段，可以重载这个变量
    column_exclude_list = (
        'password_hash', 'role'
    )


class OtherView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False
    # 这三个变量定义管理员是否可以增删改，默认为True
    can_delete = True
    can_edit = True
    can_create = True


class FileView(FileAdmin):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


file_path = '/root/video4sex/app/static'

admin.add_view(UserView(User, db.session, name=u'用户', category=u'管理'))
admin.add_view(OtherView(FriendUrl, db.session, name=u'友链', category=u'管理'))
admin.add_view(OtherView(ShortUrl, db.session, name=u'短链', category=u'管理'))
admin.add_view(OtherView(AD600, db.session, name=u'600ad广告', category=u'管理'))
admin.add_view(FileView(file_path, '/static/', name='文件', category=u'管理'))


@app.route('/<acthon>', methods=['POST', 'GET'])
@login_required
@admin_required
def reboot(acthon):
    if request.method == "POST":
        if acthon == 'reboot':
            subprocess.Popen(['reboot'])
            flash('正在重启系统！')
        if acthon == 'restart':
            subprocess.Popen(
                ['super_restart', 'online'])
            flash('正在重启网站！')
        if acthon == 'stop':
            subprocess.Popen(
                ['super_stop', 'online'])
            flash('正在重启网站！')
        if acthon == 'updatecl':
            subprocess.Popen(
                ['python', '/root/video4sex/cl1024.py'])
            flash('正在重启网站！')
        if acthon == 'washcl':
            subprocess.Popen(
                ['python', '/root/video4sex/wash_cl.py'])
            flash('正在重启网站！')
        if acthon == 'updateonline':
            subprocess.Popen(
                ['python', '/root/video4sex/qyule.py'])
            flash('正在重启网站！')
    return redirect(url_for('online.index'))


@app.route('/updateonlineurl', methods=['POST', 'GET'])
@login_required
@admin_required
def updateonlineurl():
    if request.method == 'POST':
        flag = request.form.get('flag')
        url = request.form.get('url')
        isvalid = request.form.get('isvalid', type=int)
        db.session.execute(
            'update posts set zhan="%s",isvalid=%d  where flag="%s";' % (url, isvalid, flag))
        db.session.commit()
        redirect(url_for('.updateonlineurl'))
    flags = db.session.query(Post.flag.distinct().label('flag')).all()
    flags = [flag[0] for flag in flags]
    zhans = [Post.query.filter_by(flag=flag).first() for flag in flags]
    return render_template('admin/onlineurl.html', zhans=zhans)


@app.route('/goto/<short>')
def gotoshort(short):
    short_url = ShortUrl.query.filter_by(short_url=short).first()
    if short_url is not None:
        return redirect(short_url.url)
    else:
        flash('无效链接')
        return redirect(url_for('online.index'))
