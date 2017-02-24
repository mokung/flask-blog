import hashlib
import time
import uuid
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.orm import session

from app import db, login_manager


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(50), nullable=False, primary_key=True, default=next_id)
    email = db.Column(db.String(50), nullable=False, unique=True, index=True)
    passwd = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    image = db.Column(db.String(500), nullable=False, default='/static/img/user.png')
    created_time = db.Column(db.DateTime, nullable=False, default=now)

    def register(self):
        self.id = next_id()
        sha1_pw = '%s:%s' % (self.id, self.passwd)
        self.passwd = hashlib.sha1(sha1_pw.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()

    def login(self, response, max_age=86400):
        expires = str(int(time.time() + max_age))
        s = '%s-%s-%s-%s' % (self.id, self.passwd, expires, current_app.config['COOKIE_KEY'])
        L = [self.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
        response.set_cookie(current_app.config['COOKIE_NAME'], '-'.join(L), max_age, httponly=True)
        return response

    def verify_password(self, password):
        sha1_pw = '%s:%s' % (self.id, password)
        passwd = hashlib.sha1(sha1_pw.encode('utf-8')).hexdigest()
        return self.passwd == passwd



class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.String(50), nullable=False, primary_key=True, default=next_id)
    user_id = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    user_image = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    created_time = db.Column(db.String(20), nullable=False, default=now)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.String(50), nullable=False, primary_key=True, default=next_id)
    blog_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    user_image = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    created_time = db.Column(db.String(20), nullable=False, default=now)


@login_manager.user_loader
def load_user(userid):
    #: Flask Peewee used here to return the user object
    return User.query.filter_by(id=userid).first()
