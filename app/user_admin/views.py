#-*- coding=utf-8 -*-
import datetime
from flask import jsonify, redirect, render_template, request, session, flash, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user
from . import user_admin
from .. import db
from ..models import *
from .forms import *
from ..email import *


@user_admin.route('/user/<userid>')
def user(userid):
    user = User.query.filter_by(id=userid).first()
    page = request.args.get('page', 1, type=int)
    if user is None:
        abort(404)
    pagination = user.viewtimes.order_by(ViewHistory.last_seen.desc()).paginate(
        page, per_page=20, error_out=False)
    posts = pagination.items
    return render_template('user_admin/user.html', user=user, posts=posts, pagination=pagination)
