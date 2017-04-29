import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'views.login'
    bootstrap.init_app(app)

    from app.routes.views import views
    app.register_blueprint(views)
    from app.routes.auth import auth
    app.register_blueprint(auth)
    from app.routes.api import api
    app.register_blueprint(api)
    return app


app = create_app('development')
