import re

# 检查字符串是否为空
from flask import flash

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


def check_empty(**kw):
    for key, string in kw.items():
        if not string or not string.strip():
            flash('%s cannot be empty.' % key)

def check_email_and_passwd(email, passwd):
    if not email or not _RE_EMAIL.match(email):
        flash('Invalid email')
    if not passwd or not _RE_SHA1.match(passwd):
        flash('Invalid password')