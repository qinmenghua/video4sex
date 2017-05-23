# -*- coding=utf-8 -*-
from flask import Blueprint

user_admin = Blueprint('user_admin', __name__)

from . import views, forms
