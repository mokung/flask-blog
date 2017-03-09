from flask import Blueprint, render_template, request, app
from flask import Response
from flask import flash
from flask import url_for
from flask_login import login_required
from werkzeug.utils import redirect

from app.checker import setPositive, Paginate, check_admin
from app.models import Blog, Comment, User

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template('index.html')


@views.route('/login')
def login():
    return render_template('login.html')


@views.route('/signup')
def signup():
    return render_template('signup.html')


@views.route('/blogs')
def blogs():
    page = setPositive(request.args.get('page'))
    size = setPositive(request.args.get('size'), 10)
    p = Paginate(Blog.query.count(), page, size)
    blogs = Blog.query.filter_by(is_deleted=False).order_by(Blog.created_time.desc()).offset(p.offset).limit(p.limit).all()
    admin = check_admin()
    return render_template('blogs.html', blogs=blogs, page=p, admin=admin)


@views.route('/blog/<blog_id>')
def blog(blog_id):
    blog = Blog.query.filter_by(id=blog_id).first()
    comments = Comment.get_comments_by_blog_id(blog_id)
    admin = check_admin()
    return render_template('blog.html', blog=blog, comments=comments, admin=admin)


@views.route('/edit/<blog_id>')
@login_required
def edit(blog_id):
    if not check_admin():
        flash('没有访问权限！')
        return redirect(url_for('views.blogs'))
    blog = Blog.query.filter_by(id=blog_id).first()
    return render_template('edit.html', blog=blog)


@views.route('/post')
@login_required
def post():
    if not check_admin():
        flash('没有访问权限！')
        return redirect(url_for('views.blogs'))
    return render_template('edit.html')


@views.route('/search')
def search():
    keyword = request.args.get("keyword")
    page = setPositive(request.args.get('page'))
    size = setPositive(request.args.get('size'), 10)
    p = Paginate(Blog.query.filter(Blog.title.ilike("%"+keyword+"%"), Blog.is_deleted==False).count(), page, size)
    blogs = Blog.query.filter(Blog.title.ilike("%"+keyword+"%"), Blog.is_deleted==False).order_by(Blog.created_time.desc()).offset(p.offset).limit(p.limit).all()
    admin = check_admin()
    return render_template('blogs.html', blogs=blogs, page=p, admin=admin ,keyword = keyword)