import re

from flask import flash
from flask_login import current_user

from app.models import User

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


class Paginate(object):
    def __init__(self, item_count, index=1, size=10):
        self.last = item_count // size + (1 if item_count % size > 0 else 0)
        self.index = min(index, self.last) if item_count > 0 else 1
        self.offset = size * (index - 1)
        self.limit = size


def toJson(object):
    result = {}
    for over_name in dir(object):
        if not over_name.startswith("_"):
            result[over_name] = object.over_name
    return result


def check_empty(**kw):
    for key, string in kw.items():
        if not string or not string.strip():
            flash('%s cannot be empty.' % key)


def check_email_and_passwd(email, passwd):
    if not email or not _RE_EMAIL.match(email):
        flash('Invalid email')
    if not passwd or not _RE_SHA1.match(passwd):
        flash('Invalid password')


def setPositive(numStr, default=1):
    try:
        num = int(numStr)
    except:
        return default
    return num if num > 0 else default


def check_admin():
    admin = User.is_admin(current_user)
    return admin
