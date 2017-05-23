#-*- coding=utf-8 -*-
import datetime
from flask import jsonify, redirect, render_template, request, session, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import *
from .forms import *
from ..email import *

# AUTH

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            session['logged_in'] = True
            session['admin'] = False
            if user.id == 1:
                session['admin'] = True
            session.permanent = True
            flash('登陆成功')
            return redirect(url_for('main.home'))
        else:
            flash('邮箱或密码错误')
            return redirect(url_for('auth.login'))
    return render_template('admin/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('logged_in', None)
    session.pop('admin', None)
    flash('你已经注销！')
    return redirect(url_for('main.home'))


@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # code=InviteCode.query.filter_by(code=form.invitecode.data).first()
        isvip = True
        # if code is not None and code.isvalid:
        if isvip:
            # code.isvalid=False
            # db.session.add(code)
            # db.session.commit()
            email = form.email.data
            username = form.username.data
            password = form.password.data
            user = User(email=email, username=username,
                        password=password, isvip=False)
            db.session.add(user)
            db.session.commit()
            flash('注册成功')
            return redirect(url_for('auth.login'))
        else:
            flash('无效邀请码')
            return redirect(url_for('auth.register'))
    return render_template('admin/register.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('修改密码成功！')
            return redirect(url_for('main.home'))
        else:
            flash('无效密码')
            return redirect(url_for('auth.change_password'))
    return render_template("admin/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重设密码',
                       'admin/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
            flash('重设密码邮件已经发送到邮箱')
        else:
            flash('邮箱不存在')
        return redirect(url_for('main.home'))
    return render_template('admin/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.home'))
        if user.reset_password(token, form.password.data):
            flash('密码已更新')
            return redirect(url_for('main.home'))
        else:
            return redirect(url_for('main.home'))
    return render_template('admin/reset_password.html', form=form)
