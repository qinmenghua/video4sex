#-*- coding=utf-8 -*-
from flask import jsonify, redirect, render_template, request, url_for, flash, session, jsonify, g
from flask_login import login_required, current_user
from . import pioneer
from .. import db
from ..models import *
from ..auth.forms import *
import random
from .. import logger
from .forms import CodeForm


@pioneer.route('/pioneer_proj', methods=['GET', 'POST'])
@login_required
def pioneer_project():
    form = CodeForm()
    print 'pioneer project'
    if form.validate_on_submit():
        print 'pioneer project 22'
        code = form.code.data
        userid = current_user.id
        print 'code:%s, user:%s' % (code, userid)
        submit_code = PioneerCode.query.filter_by(code=code).first()
        if submit_code is None:
            flash('礼品卡不存在')
            return redirect(url_for('pioneer.pioneer_project'))
        user = User.query.filter_by(id=int(userid)).first()
        user.jifen += submit_code.jifen
        submit_code.isvalid = False
        db.session.add(user)
        db.session.add(submit_code)
        db.session.commit()
        flash('兑换成功')
        return redirect(url_for('pioneer.pioneer_project'))
    return render_template('pioneer/index.html', form=form)


@pioneer.route('/join_pioneer', methods=['POST'])
@login_required
def join_pioneer():
    userid = request.form.get('userid')
    user = User.query.filter_by(id=userid).first()
    if user.jifen >= PioneerNeed.query.first().jifen:
        user.isvip = True
        db.session.add(user)
        db.session.commit()
        PioneerNeed.update()
        logger.info('%(username)s:%(userid)s join the pioneer project' %
                    {'username': user.username, 'userid': userid})
        return jsonify(dict(msg='祝贺您，您已经是先锋计划的成员了！'))
    else:
        logger.info('%(username)s:%(userid)s fail to join the pioneer project' % {
                    'username': user.username, 'userid': userid})
        return jsonify(dict(msg='作弊是不对的！'))
