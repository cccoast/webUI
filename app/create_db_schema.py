from werkzeug.security import generate_password_hash, check_password_hash

import sys
sys.path.append('../../')
from future_mysql import dbBase
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Index, Float, Boolean
from sqlalchemy import Table

class User(dbBase.DB_BASE):

    def __init__(self):
        db_name = 'flask'
        table_name = 'password'
        super(User, self).__init__(db_name)

        self.table_struct = Table(table_name, self.meta,
                                  Column(
                                      'id',
                                      Integer,
                                      primary_key=True,
                                      autoincrement=False),
                                  Column('username', String(64)),
                                  Column('password_hash', String(128)))

    def create_table(self):
        self.user_struct = self.quick_map(self.table_struct)

if __name__ == '__main__':
    user = User()
    user.create_table()
    
    indict = {
        'id': 3,
        'username': 'guest',
        'password_hash': generate_password_hash('123456')
    }
    user.insert_dictlike(user.user_struct, indict)
    print 'successed!'
    