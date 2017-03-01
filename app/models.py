from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'password'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    
    import sys
    sys.path.append('../../')
    from future_mysql import dbBase
    from sqlalchemy import Column, Integer, String, DateTime, Numeric, Index, Float, Boolean
    from sqlalchemy import Table
    
    class User(dbBase.DB_BASE):
    
        def __init__(self):
            db_name = 'flask'
            table_name = 'password'
            super(User,self).__init__(db_name)
            
            self.table_struct = Table(table_name,self.meta,
                        Column('id',Integer,primary_key = True,autoincrement = False ),
                        Column('username',String(64)),
                        Column('password_hash',String(128))
                        )
            
        def create_table(self):
            self.user_struct = self.quick_map(self.table_struct)
            
    user = User()
    user.create_table()
    
    indict = {'id':1,'username':'xudi','password_hash':generate_password_hash('123456')}
    user.insert_dictlike(user.user_struct,indict)
    
    