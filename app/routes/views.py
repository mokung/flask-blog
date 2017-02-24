from flask import Blueprint, render_template
from flask_login import login_required

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def index():
    return render_template('index.html')


@views.route('/login')
def login():
    return render_template('login.html')


@views.route('/signup')
def signup():
    return render_template('signup.html')
