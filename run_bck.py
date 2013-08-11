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
import run_bck_config

# Main
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.info('Start')

for bckdir in bckdir_list:
    bckdir_base = os.path.basename(os.path.normpath(bckdir))
    logging.debug('Backup ' + bckdir_base)
    my_backup = BckTarGroup(bckdir_base, bckdir, dest_dir, work_dir, password)
    my_backup.create()