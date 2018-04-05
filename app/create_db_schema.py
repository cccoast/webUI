from werkzeug.security import generate_password_hash, check_password_hash

import sys
if '../../' not in sys.path:
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
                                  Column('id',Integer,primary_key=True,autoincrement=False),
                                  Column('username', String(64)),
                                  Column('work_unit',String(64)),
                                  Column('password_hash', String(128)))

    def create_table(self):
        self.user_struct = self.quick_map(self.table_struct)
        
class Task(dbBase.DB_BASE):
    
    def __init__(self):
        db_name = 'flask'
        table_name = 'task'
        super(User, self).__init__(db_name)

        self.table_struct = Table(table_name, self.meta,
                                  Column('username', String(64),primary_key=True,),
                                  Column('work_unit', String(64)),
                                  Column('task_name',String(64)),
                                  )

    def create_table(self):
        self.user_struct = self.quick_map(self.table_struct)

def create_user_table():
    user = User()
    user.create_table()
    indict = {
        'id': 1,
        'username': 'xudi',
        'password_hash': generate_password_hash('123456'),
        'work_unit':'pbc'
    }
    user.insert_dictlike(user.user_struct, indict)
    print 'successed!'
    
def create_task_table():
    pass

if __name__ == '__main__':
    create_user_table()
    