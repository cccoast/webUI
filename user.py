import sys
sys.path.append('../')
from future_mysql import dbBase 

from sqlalchemy import Column, Integer, String, DateTime, Numeric, Index, Float
from sqlalchemy import Table

import werkzeug.security as myhash

class User(dbBase.DB_BASE):
    
    def __init__(self):
        db_name = 'user'
        table_name = 'password'
        super(User,self).__init__(db_name)
        
        self.table_struct = Table(table_name,self.meta,
                     Column('name',String(20),primary_key = True),
                     Column('password',String(160)),
                    )
        
    def create_table(self):
        self.user_struct = self.quick_map(self.table_struct)
        
    def insert_user(self,name,pwd):
        indict = {'name':name,'password':myhash.generate_password_hash(pwd)}
        user.insert_dictlike(user.user_struct,indict)
        
    def check_user(self,name,pwd):
        session = self.get_session()
        re = session.query(self.user_struct).filter_by(name = name).all()
        ret = False
        for i in re:
            if myhash.check_password_hash(i.password, pwd):
                ret = True
            else:
                ret = False
        session.close()
        return ret
        
if __name__ == '__main__':
    user = User()
    user.create_table()
    user.insert_user('lyx','123456')
    print user.check_user('lyx','123456')

    