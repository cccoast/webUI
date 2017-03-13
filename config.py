import os
from flask_uploads import DEFAULTS, TEXT
basedir = os.path.abspath(os.path.dirname(__file__))
db_name = 'flask'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOADED_CFG_DEST = os.path.join( os.getcwd(),'app','static','cfgs' ) 
    UPLOADED_CFG_ALLOW = TEXT
    
    @staticmethod
    def init_app(app):
        pass
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://xudi:123456@127.0.0.1:3306/{0}".format(db_name)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://xudi:123456@127.0.0.1:3306/{0}".format(db_name)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://xudi:123456@127.0.0.1:3306/{0}".format(db_name)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
