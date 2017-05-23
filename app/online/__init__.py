# -*- coding=utf-8 -*-
from flask import Blueprint

online=Blueprint('online',__name__)

from . import views
