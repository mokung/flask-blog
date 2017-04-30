import hashlib
import time
import uuid
from flask import current_app
from flask_login import UserMixin


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

    @property
    def is_admin(self):
        return not self.is_anonymous and self.admin == 1


class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.String(50), nullable=False, primary_key=True, default=next_id)
    user_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    created_time = db.Column(db.String(20), nullable=False, default=now)
    is_deleted = db.Column(db.Boolean, nullable=True, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def update(cls, blog):
        db.session.merge(blog)
        db.session.commit()

    def tojosn(self):
        return {
            'id': self.id,
            'title' : self.title,
            'summary':self.summary,
            'content':self.content,
            'created_time':self.created_time.strftime('%Y-%m-%d %H:%M:%S')
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.String(50), nullable=False, primary_key=True, default=next_id)
    blog_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    created_time = db.Column(db.String(20), nullable=False, default=now)
    is_deleted = db.Column(db.Boolean, nullable=True, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(comment):
        db.session.merge(comment)
        db.session.commit()

    @classmethod
    def get_comments_by_blog_id(cls, blog_id):
        result = db.session.query(Comment.id, Comment.content, Comment.created_time, User.name). \
            join(User, Comment.user_id == User.id).filter(Comment.blog_id == blog_id, Comment.is_deleted==0). \
            order_by(Comment.created_time.desc()).all()
        return result


@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=userid).first()
