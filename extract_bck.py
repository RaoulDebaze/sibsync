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

srce_dir = bckdir_list[0]
extract_dir = os.path.join(srce_dir, 'tmp')
if not os.path.exists(extract_dir):
    os.makedirs(extract_dir)

bck_name = os.path.basename(os.path.normpath(srce_dir))
bck_list = get_bcktargroups(bck_name, dest_dir)
if bck_list:
    last_bck = bck_list[-1]
    my_backup = BckTarGroup(last_bck, \
                            srce_dir, dest_dir, work_dir, password)
    my_backup.extract(extract_dir)

