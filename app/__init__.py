#-*- coding=utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_admin import Admin
import logging
import datetime
# 日志记录
logger = logging.getLogger("video4sex")
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler("/root/video4sex/logs/video4sex_%(date)s.log" %
                         {'date': datetime.datetime.now().strftime('%Y-%m-%d')})
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


app = Flask(__name__)
app.config.from_object('config')
login_manager = LoginManager(app)
login_manager.session_protect = 'strong'
login_manager.login_view = 'auth.login'
admin = Admin(app)
bootstrap = Bootstrap(app)
mail = Mail(app)
pagedown = PageDown(app)
db = SQLAlchemy(app, use_native_unicode='utf8')

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .online import online as online_blueprint
app.register_blueprint(online_blueprint)

from .cl1024 import cl as cl_blueprint
app.register_blueprint(cl_blueprint)


from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)


from .pioneer import pioneer as pioneer_blueprint
app.register_blueprint(pioneer_blueprint)

from .user_admin import user_admin as user_admin_blueprint
app.register_blueprint(user_admin_blueprint)


from app import views
