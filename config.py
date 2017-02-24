import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'qfsdferfbzzzz'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost:3306/awesome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}