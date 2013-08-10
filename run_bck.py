#! /usr/bin/env python

import filecmp
import getpass
import logging
import os
import shutil
import socket
import sys
import time
from bck4sync import BckTarGroup

# Main
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.info('Start')

logging.debug('Setting global variables')
base_bck_dir = '/Users/Shared/Sauvegardes'
ref_dir = os.getcwd()
user = getpass.getuser()
host = socket.gethostname()
dest_dir = os.path.join(base_bck_dir, host, user)
work_dir = os.path.join(base_bck_dir, '.bck4sync')
extract_dir = os.path.join(base_bck_dir, 'restore')

password = 'changeme'

bckdir_list = [\
        '/path/to/dir1', \
        '/path/to/dir2', \
        '/path/to/dir3', \
        '/path/to/dir4']
for bckdir in bckdir_list:
    bckdir_base = os.path.basename(os.path.normpath(bckdir))
    logging.debug('Backup ' + bckdir_base)
    my_backup = BckTarGroup(bckdir_base, bckdir, dest_dir, work_dir, password)
    my_backup.create()