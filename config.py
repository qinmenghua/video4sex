import os
basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'SSDFDSFDFD'
SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost/web'
SQLALCHEMY_TRACK_MODIFICATIONS = True
debug = True
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'yourmail@gmail.com'
MAIL_PASSWORD = 'yourpassword'
#LDAP_LOGIN_VIEW = 'auth.login'
