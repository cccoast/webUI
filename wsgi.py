import os
from app import create_app

xapp = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    xapp.run('127.0.0.1',5000,True)