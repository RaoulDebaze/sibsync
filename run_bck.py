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
# Import configuration
import bck_config
from bck4sync import get_bcktargroups

bckdir_list = bck_config.bckdir_list
dest_dir = bck_config.dest_dir
work_dir = bck_config.work_dir
password = bck_config.password
# Main
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.info('Start')

if not os.path.exists(work_dir):
    os.makedirs(work_dir)

for bckdir in bckdir_list:
    bckdir_base = os.path.basename(os.path.normpath(bckdir))
    bck_list = get_bcktargroups(bckdir_base, dest_dir)
    if bck_list:
        last_bck = bck_list[-1]
        my_backup = BckTarGroup(last_bck, \
                bckdir, dest_dir, work_dir, password)
        my_backup.update()
    else:
        logging.debug('Backup ' + bckdir_base)
        my_backup = BckTarGroup(bckdir_base, \
                bckdir, dest_dir, work_dir, password)
        my_backup.create()
