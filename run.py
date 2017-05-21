import os
from app import xapp
import sys
upper_abs_path = os.path.sep.join((os.path.abspath(os.curdir).split(os.path.sep)[:-1]))
pkg_path = os.path.join(upper_abs_path,'generate_data_block')
# print pkg_path
if pkg_path not in sys.path:
    sys.path.append(pkg_path)

from transfer import server_addr

if __name__ == '__main__':
    xapp.run(server_addr,5000,True)