#! /usr/bin/env python

import getpass
import os
import socket

base_bck_dir = '/Users/Shared/Sauvegardes'
user = getpass.getuser()
host = socket.gethostname()
dest_dir = os.path.join(base_bck_dir, host, user)
work_dir = os.path.join('/Users/simon/Desktop', '.bck4sync')

password = 'changeme'

bckdir_list = [\
        '/Users/simon/Desktop', \
        '/Users/simon/Documents', \
        '/Users/simon/Library', \
        '/Users/simon/Pictures']
