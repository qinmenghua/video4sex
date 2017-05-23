# -*- coding=utf-8 -*-
from flask import Blueprint

cl=Blueprint('cl',__name__)

from . import views
