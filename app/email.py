#coding;utf-8
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message('Tumbzzc' + subject,
                  sender='admin@admin.tumbzzc.com', recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
