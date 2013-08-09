#! /usr/bin/env python

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
logging.info('Start Tests')

logging.debug('Setting global variables')
dir_to_backup = '/root/res/test'
base_bck_dir = '/root/res/bck'
#dir_to_backup = '/Users/simon/Partages/Test'
#base_bck_dir = '/Users/simon/Partages/Sauvegardes'
ref_dir = os.getcwd()
user = getpass.getuser()
host = socket.gethostname()
srce_dir = dir_to_backup
dest_dir = os.path.join(base_bck_dir, host, user)
work_dir = os.path.join(base_bck_dir, '.bck4sync')
extract_dir = os.path.join(base_bck_dir, 'ex_dir')

password = 'changeme'

def rm_dir_content(dir_path):
    print "rm: " + dir_path
    all_dir = []
    for root_dir, dir_names, file_names in os.walk(dir_path):
        for file_name in file_names:
            path = os.path.join(root_dir, file_name)
            os.remove(path)
        for dir_name in dir_names:
            path = os.path.join(root_dir, dir_name)
            all_dir.append(path)
    print all_dir
    for dir_name in all_dir:
        os.rmdir(path)

def take_fs_photo():
    files = []
    os.chdir(srce_dir)
    for root_dir, dir_names, file_names in os.walk('.'):
        for file_name in (file_names + dir_names):
            try:
                file_path = os.path.join(root_dir, file_name)
                if os.path.isdir(file_path):
                    file_size = 0
                else:
                    file_size = os.stat(file_path).st_size
                files.append({'path': os.path.normpath(file_path),
                              'mtime': int(os.stat(file_path).st_mtime),
                              'size': file_size})
            except OSError:
                logging.debug('Error on file ' + file_name)
        
    # Sort list by files date
    return sorted(files, key=lambda mtime: mtime['mtime'])

# Test 1
# Create a new backup
# Preparation 1
#time.sleep(1)
if os.path.exists(dest_dir):
    rm_dir_content(dest_dir)
else:
    os.makedirs(dest_dir)
if os.path.exists(work_dir):
    rm_dir_content(work_dir)
else:
    os.makedirs(work_dir)
# Reinitialize dir_to_backup
#if os.path.exists(dir_to_backup):
#    rm_dir_content(dir_to_backup)
#else:
#    os.makedirs(dir_to_backup)
shutil.rmtree(dir_to_backup)
shutil.copytree(os.path.join(ref_dir, '0'), dir_to_backup)

fs_photo = take_fs_photo()
# Test
my_backup = BckTarGroup('sib', srce_dir, dest_dir, work_dir, password)
my_backup.create()
# Result 1
result = True
backup_name = my_backup.name
if not my_backup.is_complete():
    result = False
else:
    bck_submembers = my_backup.getsubmembers()
    if fs_photo != bck_submembers:
        result = False
# Output 1
if result:
    print 'Test 1: OK\n\n'
else:
    print 'Test 1: KO'
    sys.exit(1)

time.sleep(1)
# Test 2
# Read an existing backup
# Preparation
print '-'*5 + ' Test 2 ' + '-'*5
del my_backup
fs_photo = take_fs_photo()
# Test
logging.debug('backup_name = ' + backup_name)
my_backup = BckTarGroup(backup_name, srce_dir, dest_dir, work_dir, password)
my_backup.print_members()
bck_submembers2 = my_backup.getsubmembers()
# Result
result = True
if fs_photo != bck_submembers2:
    result = False
# Output
if result:
    print 'Test 2: OK\n\n'
else:
    print 'Test 2: KO'
    sys.exit(2)   

time.sleep(1)
# Test 3
# Update an existing backup with the last member not full
# Preparation
print '-'*5 + ' Test 3 ' + '-'*5
os.utime(os.path.join(srce_dir, 'dir2', 'file21'), None)   
fs_photo3 = take_fs_photo()
# Test
#print backup_name
#my_backup = BckTarGroup(backup_name, srce_dir, dest_dir, work_dir, password)
my_backup3 = my_backup.update()
my_backup3.print_members()
bck_submembers = my_backup.getsubmembers()
bck_submembers3 = my_backup3.getsubmembers()
# Result
result = True
if fs_photo != bck_submembers:
    logging.debug('Members of first backup as been updated !')
    result = False
elif fs_photo3 != bck_submembers3:
    logging.debug('New backup does not reflect currestn file system !')
    result = False
# Output
if result:
    print 'Test 3: OK\n\n'
else:
    print 'Test 3: KO'
    sys.exit(3)   

time.sleep(1)
# Test 4
# Update an existing backup but not change has been dont on the file system
# Preparation
print '-'*5 + ' Test 4 ' + '-'*5
# Test
#print backup_name
#my_backup = BckTarGroup(backup_name, srce_dir, dest_dir, work_dir, password)
my_backup4 = my_backup3.update()
bck_submembers4 = my_backup4.getsubmembers()
my_backup4.print_members()
# Result
result = True
if bck_submembers4 != bck_submembers3:
    logging.debug('Members of updated backup should not been different \
            from original backup')
    result = False
# Output
if result:
    print 'Test 4: OK\n\n'
else:
    print 'Test 4: KO'
    sys.exit(3)   

time.sleep(1)
# Test 5
# Update an existing backup where all members of a tar has been updated
# Preparation
print '-'*5 + ' Test 5 ' + '-'*5
os.utime(os.path.join(srce_dir, 'dir2', 'file6'), None)   
os.utime(os.path.join(srce_dir, 'dir2', 'file7'), None)   
os.utime(os.path.join(srce_dir, 'dir2', 'file9'), None)   
os.utime(os.path.join(srce_dir, 'dir2', 'file10'), None)
fs_photo5 = take_fs_photo()
# Test
#print backup_name
#my_backup = BckTarGroup(backup_name, srce_dir, dest_dir, work_dir, password)
my_backup5 = my_backup4.update()
bck_members5 = my_backup5.getmembers()
my_backup5.print_members()
bck_photo5 = [ item for sublist in bck_members5 for item in sublist ]
# Result
result = True
if bck_photo5 != fs_photo5:
    logging.debug('Backup does not reflect the file system')
    result = False
elif my_backup5.bcktar_members[2]:
    logging.debug('Tar 3 is not empty')
    result = False
# Output
if result:
    print 'Test 5: OK\n\n'
else:
    print 'Test 5: KO'
    sys.exit(3)   
