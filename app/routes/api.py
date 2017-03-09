import os

import re

from flask import make_response, jsonify

import app
from flask import Blueprint, request, redirect, url_for, render_template
from flask import Response, flash
from flask import json
from config import basedir
from app.Uploader import Uploader
from flask_login import current_user, login_required
from app.models import Blog, User, Comment
from app.checker import check_admin, toJson

api = Blueprint('api', __name__, url_prefix="/api")


@api.route('/post', methods=['POST'])
@login_required
def api_post():
    if not check_admin():
        flash('没有访问权限！')
        return redirect(url_for('views.blogs'))
    user_id = current_user.get_id()
    title = request.form["title"]
    summary = request.form["summary"]
    content = request.form["content"]
    if not title or not content:
        flash('没有标题或内容为空！')
        return False
    blog = Blog(user_id=user_id, title=title, summary=summary, content=content)
    blog.save()
    return redirect(request.args.get('next') or url_for('views.blogs'))


@api.route('/search')
def api_search():
    keyword = request.args.get("keyword")
    blogs = Blog.query.filter(Blog.title.ilike("%"+keyword+"%")).all()
    result = []
    for blog in blogs:
        result.append(blog.tojosn())
    return json.dumps(result)


@api.route('/edit/<blog_id>', methods=['POST'])
@login_required
def api_edit(blog_id):
    if not check_admin():
        flash('没有访问权限！')
        return redirect(url_for('views.blogs'))
    title = request.form["title"]
    summary = request.form["summary"]
    content = request.form["content"]
    if not title or not content:
        flash('没有标题或内容为空！')
        return False
    blog = Blog(id=blog_id, title=title, summary=summary, content=content)
    Blog.update(blog)
    return redirect(request.args.get('next') or url_for('views.blog', blog_id=blog_id))


@api.route('/delete/blog/<blog_id>')
@login_required
def api_delete_blog(blog_id):
    if not check_admin():
        flash('没有访问权限！')
        return redirect(url_for('views.blogs'))
    blog = Blog(id=blog_id, is_deleted=True)
    Blog.update(blog)
    return redirect(request.args.get('next') or url_for('views.blogs'))


@api.route('/comment/<blog_id>', methods=['POST'])
@login_required
def api_comment(blog_id):
    user_id = current_user.get_id()
    content = request.form["content"]
    if not blog_id or not content or content == "":
        flash('评论内容为空！')
        return False
    comment = Comment(blog_id=blog_id, user_id=user_id, content=content)
    comment.save()
    return redirect(request.args.get('next') or url_for('views.index'))


@api.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload():
    action = request.args.get('action')

    # 解析JSON格式的配置文件
    with open(os.path.join(basedir, 'app', 'static', 'ueditor', 'php',
                           'config.json'), encoding='utf-8') as fp:
        # 删除注释
        josnconent = re.sub(r'\/\*.*\*\/', '', fp.read())
    CONFIG = json.loads(josnconent)

    if action == 'config':
        # 初始化时，返回配置文件给客户端
        result = CONFIG
    elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
        # 图片、文件、视频上传
        if action == 'uploadimage':
            fieldName = CONFIG.get('imageFieldName')
            config = {
                "pathFormat": CONFIG['imagePathFormat'],
                "maxSize": CONFIG['imageMaxSize'],
                "allowFiles": CONFIG['imageAllowFiles']
            }
        elif action == 'uploadvideo':
            fieldName = CONFIG.get('videoFieldName')
            config = {
                "pathFormat": CONFIG['videoPathFormat'],
                "maxSize": CONFIG['videoMaxSize'],
                "allowFiles": CONFIG['videoAllowFiles']
            }
        else:
            fieldName = CONFIG.get('fileFieldName')
            config = {
                "pathFormat": CONFIG['filePathFormat'],
                "maxSize": CONFIG['fileMaxSize'],
                "allowFiles": CONFIG['fileAllowFiles']
            }
        if fieldName in request.files:
            field = request.files[fieldName]

            uploader = Uploader(field, config, os.path.join(basedir, 'app', 'static'))
            result = uploader.getFileInfo()
        else:
            result = dict(state='上传接口出错')
    elif action in ('uploadscrawl'):
        # 涂鸦上传
        fieldName = CONFIG.get('scrawlFieldName')
        config = {
            "pathFormat": CONFIG.get('scrawlPathFormat'),
            "maxSize": CONFIG.get('scrawlMaxSize'),
            "allowFiles": CONFIG.get('scrawlAllowFiles'),
            "oriName": "scrawl.png"
        }
        if fieldName in request.form:
            field = request.form[fieldName]
            uploader = Uploader(field, config, os.path.join(basedir, 'app', 'static'), 'base64')
            result = uploader.getFileInfo()
        else:
            result = dict(state='上传接口出错')
    elif action in ('catchimage'):
        config = {
            "pathFormat": CONFIG['catcherPathFormat'],
            "maxSize": CONFIG['catcherMaxSize'],
            "allowFiles": CONFIG['catcherAllowFiles'],
            "oriName": "remote.png"
        }
        fieldName = CONFIG['catcherFieldName']
        if fieldName in request.form:
            # 这里比较奇怪，远程抓图提交的表单名称不是这个
            source = []
        elif '%s[]' % fieldName in request.form:
            # 而是这个
            source = request.form.getlist('%s[]' % fieldName)
        _list = []
        for imgurl in source:
            uploader = Uploader(imgurl, config, app.static_folder, 'remote')
            info = uploader.getFileInfo()
            _list.append({
                'state': info['state'],
                'url': info['url'],
                'original': info['original'],
                'source': imgurl,
            })
        result = dict(state='SUCCESS', list=_list) if len(_list) > 0 else dict(list=_list, state='ERROR')
    else:
        result = dict(state='上传接口出错')
    result = json.dumps(result)

    if 'callback' in request.args:
        callback = request.args.get('callback')
        if re.match(r'^[\w_]+$', callback):
            result = '%s(%s)' % (callback, result)
        else:
            result = json.dumps({'state': 'callback参数不合法'})
    res = make_response(result)
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'

    return res
