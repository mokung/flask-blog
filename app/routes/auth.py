import re
from flask import Blueprint, request, redirect, url_for, render_template
from flask import Response,flash
from flask_login import login_user, logout_user
from app.models import User
from app.checker import check_empty,check_email_and_passwd
auth = Blueprint('auth', __name__, url_prefix="/auth")

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


# 注册新用户
@auth.route('/register', methods=['POST'])
def register():
    # 检查用户名
    name = request.form['name']
    check_empty(name=name)
    email = request.form['email']
    passwd = request.form['passwd']
    check_email_and_passwd(email,passwd)
    # 检查邮箱是否已占用
    if User.query.filter_by(email=email).count():
        flash('User already exists！')
    user = User(name=name.strip(), email=email, passwd=passwd)
    user.register()
    login_user(user)
    return redirect(request.args.get('next') or url_for('views.index'))


# 登录
@auth.route('/login', methods=['POST'])
def auth_login():
    # 检查邮箱和密码的格式
    email = request.form["email"]
    passwd = request.form["passwd"]
    check_email_and_passwd(email, passwd)
    user = User.query.filter_by(email=email).first()
    if user is not None and user.verify_password(passwd):
        login_user(user)
        return redirect(request.args.get('next') or url_for('views.index'))
    return Response("Fail！")

# 登出
@auth.route('/logout')
def logout():
    # 检查邮箱和密码的格式
    logout_user()
    return redirect(url_for('views.index'))
