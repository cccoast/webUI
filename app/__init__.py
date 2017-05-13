from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_uploads import UploadSet, configure_uploads, patch_request_class, TEXT, DEFAULTS, IMAGES

import os
import sys
upper_abs_path = os.path.sep.join((os.path.abspath(os.curdir).split(os.path.sep)[:-1]))
pkg_path = os.path.join(upper_abs_path,'generate_data_block')
if pkg_path not in sys.path:
    sys.path.append(pkg_path)
from ipc_util import PRC_Clinet,getUploadAddr_back,getDownloadAddr_front

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
ufile = UploadSet('CFG', TEXT)

def create_rpc_client():
    rpc_client = PRC_Clinet()
    
    recv_addr = getUploadAddr_back()
    send_addr = getDownloadAddr_front()
    
    print 'recv_addr = ',recv_addr
    print 'send_addr = ',send_addr
    
    rpc_client.connect(recv_addr, send_addr)
    rpc_client.start()
    return rpc_client

def create_app(config_name):
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    configure_uploads(app, ufile)
    
#     test injection
#     setattr(app, 'author_name', 'xudi')
    
    rpc_client = create_rpc_client()
    setattr(app, 'rpc_client', rpc_client)
    
    return app

xapp = create_app(os.getenv('FLASK_CONFIG') or 'default')
