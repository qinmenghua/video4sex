# -*- coding=utf-8 -*-
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from app import login_manager
import datetime
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib
import random
import string


def activation_code(length=10):
    id = random.randint(0, 99)
    prefix = hex(int(id))[2:] + 'L'
    length = length - len(prefix)
    chars = string.ascii_letters + string.digits
    return prefix + ''.join([random.choice(chars) for i in range(length)])


class Permission:
    FOLLOW = 0x01
    COMMENT = 0X02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True), 'Moderator': (Permission.FOLLOW |
                                                                     Permission.COMMENT |
                                                                     Permission.WRITE_ARTICLES |
                                                                     Permission.MODERATE_COMMENTS, False), 'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
            db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    isvip = db.Column(db.Boolean, default=False, index=True)
    avatar_hash = db.Column(db.String(32))
    jifen = db.Column(db.Integer, default=0)
    viewtimes = db.relationship('ViewHistory', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == 'video4sexroot@gmail.com':
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @staticmethod
    def remove_ban_user():
        remove_user = []
        users = User.query.filter(
            User.last_seen <= datetime.datetime.now() - datetime.timedelta(15)).all()
        for user in users:
            print 'remove user:', user.username
            remove_user.append(user.username)
            db.session.delete(user)
        db.session.commit()
        return remove_user

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def gravatar(self, size=40, default='identicon', rating='g'):
        # if request.is_secure:
        #     url = 'https://secure.gravatar.com/avatar'
        # else:
        #     url = 'http://www.gravatar.com/avatar'
        url = 'http://gravatar.duoshuo.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    @staticmethod
    def insert_avatar():
        for user in User.query.all():
            if user.email is not None and user.avatar_hash is None:
                user.avatar_hash = hashlib.md5(
                    user.email.encode('utf-8')).hexdigest()
                db.session.add(user)
                db.session.commit()
    @staticmethod
    def insert_admin(email,password,username='admin'):
        admin=User(email=email,password=password,username=username,isvip=True)
        admin.role=Role.query.filter_by(permissions=0xff).first()
        db.session.add(admin)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# short_url
class ShortUrl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64))
    short_url = db.Column(db.String(64))

    def __init__(self, **kwargs):
        super(ShortUrl, self).__init__(**kwargs)


class FriendUrl(db.Model):
    __tablename__ = "friendurls"
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer)
    url = db.Column(db.String(64))
    name = db.Column(db.String(64))
    isvalid = db.Column(db.Boolean, default=True)
    isok = db.Column(db.Boolean, default=True)

    def __init__(self, **kwargs):
        super(FriendUrl, self).__init__(**kwargs)

    def __repr__(self):
        return '<%r>' % self.url

    @staticmethod
    def insert_url():
        url=Friend(order=1,url='http://www.video4sex.com',name='video4sex',isvalid=True,isok=True)
        db.session.add(url)
        db.session.commit()

class IP(db.Model):
    __tablename__ = 'userip'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64))
    date = db.Column(db.Integer)
    count = db.Column(db.Integer)

    def __init__(self, ip, date, count):
        self.ip = ip
        self.date = date
        self.count = count

    @staticmethod
    def add_count(db, ip, date):
        ip_ = IP.query.filter_by(ip=ip, date=date).first()
        if ip_ is not None:
            ip_.count += 1
            db.session.add(ip_)
            db.session.commit()
        else:
            insert_ip = IP(ip, date, 1)
            db.session.add(insert_ip)
            db.session.commit()

    def __repr__(self):
        return '<%r>' % (self.ip)


class Post(db.Model):
    __tablename__ = 'posts'
    encode = db.Column(db.String(32), primary_key=True)
    zhan = db.Column(db.String(64))
    flag = db.Column(db.String(64))
    id = db.Column(db.String(64))
    title = db.Column(db.String(64), index=True)
    picture = db.Column(db.String(200))
    video = db.Column(db.String(200), index=True)
    raw_video = db.Column(db.String(200))
    ilike = db.Column(db.Integer, default=0)
    unlike = db.Column(db.Integer, default=0)
    isvalid = db.Column(db.Integer, default=1)
    isvip = db.Column(db.Boolean, default=0)
    createtime = db.Column(db.String(64))
    viewtimes = db.Column(db.Integer, default=0)
    openload_id = db.Column(db.String(64))
    openload_url = db.Column(db.String(64))
    openload_expired = db.Column(db.DateTime())
    onlinetags = db.relationship('onlineTag', backref='post', lazy='dynamic')
    viewhistory = db.relationship(
        'ViewHistory', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)

    @staticmethod
    def add_times(db, encode):
        post = Post.query.filter_by(encode=encode).first()
        post.viewtimes += 1
        db.session.add(post)
        db.session.commit()


# online-tags
class onlineTag(db.Model):
    __tablename__ = 'onlinetags'
    autoid = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64))
    url = db.Column(db.String(64))
    encode_id = db.Column(db.String(32), db.ForeignKey(
        'posts.encode', ondelete='CASCADE', onupdate='CASCADE'))

    def __init__(self, tag, url, encode_id):
        self.tag = tag
        self.url = url
        self.encode_id = encode_id
        self.post = Post.query.filter_by(encode=encode_id).first()


# 观看记录
class ViewHistory(db.Model):
    __tablename__ = 'viewhistory'
    autoid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    encode_id = db.Column(db.String(32), db.ForeignKey(
        'posts.encode', ondelete='CASCADE', onupdate='CASCADE'))
    viewtimes = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        super(ViewHistory, self).__init__(**kwargs)

    @staticmethod
    def add_view(user_id, encode_id):
        time = datetime.datetime.utcnow()
        vh = ViewHistory.query.filter_by(
            user_id=user_id, encode_id=encode_id).first()
        if vh is None:
            vh = ViewHistory(user_id=user_id, encode_id=encode_id,
                             last_seen=time, viewtimes=1)
            db.session.add(vh)
            db.session.commit()
        else:
            vh.last_seen = time
            vh.viewtimes += 1
            db.session.commit()


# comment
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('comments.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('comments.id'),
                            primary_key=True)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    author_name = db.Column(db.String(64))
    author_email = db.Column(db.String(64))
    avatar_hash = db.Column(db.String(32))
    article_id = db.Column(db.String(32), db.ForeignKey(
        'posts.encode', ondelete='CASCADE', onupdate='CASCADE'))
    disabled = db.Column(db.Boolean, default=False)
    comment_type = db.Column(db.String(64), default='comment')
    reply_to = db.Column(db.String(128), default='notReply')

    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Comment, self).__init__(**kwargs)
        if self.author_email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.author_email.encode('utf-8')).hexdigest()

    def gravatar(self, size=40, default='identicon', rating='g'):
        # if request.is_secure:
        #     url = 'https://secure.gravatar.com/avatar'
        # else:
        #     url = 'http://www.gravatar.com/avatar'
        url = 'http://gravatar.duoshuo.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.author_email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def is_reply(self):
        if self.followed.count() == 0:
            return False
        else:
            return True
    # to confirm whether the comment is a reply or not

    def followed_name(self):
        if self.is_reply():
            return self.followed.first().followed.author_name


# cl
class clPost(db.Model):
    __tablename__ = 'clposts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), index=True)
    body = db.Column(db.Text(100000))
    forum = db.Column(db.String(20), index=True)
    createtime = db.Column(db.String(64))

    def __init__(self, id, title, body, forum, createtime):
        self.id = id
        self.title = title
        self.body = body
        self.forum = forum
        self.createtime = createtime

    def __repr__(self):
        return self.title


# 先锋计划
class PioneerCode(db.Model):
    __tablename__ = 'pioneercodes'
    autoid = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64))
    jifen = db.Column(db.Integer, default=1)
    note = db.Column(db.String(64))
    isvalid = db.Column(db.Boolean, default=True)

    def __init__(self, **kwargs):
        super(PioneerCode, self).__init__(**kwargs)

    @staticmethod
    def insert_code(jifen, num):
        for i in range(num):
            code = activation_code()
            a = PioneerCode(code=code, jifen=jifen)
            db.session.add(a)
        db.session.commit()


class PioneerNeed(db.Model):
    __tablename__ = 'pioneerneeds'
    jifen = db.Column(db.Integer, primary_key=True)

    def __init__(self, **kwargs):
        super(PioneerNeed, self).__init__(**kwargs)

    @staticmethod
    def update():
        a = PioneerNeed.query.first()
        a.jifen = User.query.filter_by(isvip=True).count() + 9
        db.session.add(a)
        db.session.commit()


# 600ad广告链接
class AD600(db.Model):
    __tablename__ = 'ad600'
    autoid = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64))
    note = db.Column(db.String(64))
    isvalid = db.Column(db.Boolean, default=True)
