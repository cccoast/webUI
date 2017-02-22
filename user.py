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
        
if __name__ == '__main__':
    user = User()
    user.create_table()
    indict = {'name':'xudi','password':myhash.generate_password_hash('123456')}
#     user.insert_dictlike(user.user_struct,indict)
    ss = user.get_session()
    re = ss.query(user.table_struct).filter_by(name = 'xudi')
    for i in re:
        print i
    ss.commit()
    ss.close()
    