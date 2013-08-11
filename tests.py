#! /usr/bin/env python

import filecmp
import getpass
import logging
import os
import shutil
import socket
import sys
import time
import bck4sync
from bck4sync import BckTarGroup
from bck4sync import get_bcktargroups

# Main
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.info('Start Tests')

logging.debug('Setting global variables')
ref_dir = os.getcwd()
dir_to_backup = os.path.join(ref_dir, 'srce_dir')
base_bck_dir = os.path.join(ref_dir, 'dest_dir')
user = getpass.getuser()
host = socket.gethostname()
srce_dir = dir_to_backup
dest_dir = os.path.join(base_bck_dir, host, user)
work_dir = os.path.join(base_bck_dir, '.bck4sync')
extract_dir = os.path.join(base_bck_dir, 'restore')

password = 'changeme'

def rm_dir_content(dir_path):
    print "rm: " + dir_path
    os.chdir(dir_path)
    all_dir = []
    for root_dir, dir_names, file_names in os.walk(dir_path):
        for dir_name in dir_names:
            if os.path.isdir(dir_name):
                shutil.rmtree(dir_name)
    for root_dir, dir_names, file_names in os.walk(dir_path):
        for file_name in file_names:
            os.remove(file_name)

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def take_fs_photo(dir_path):
    files = []
    os.chdir(dir_path)
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

# Set time of ref dir
os.utime(os.path.join(ref_dir, '0', 'file1'), \
         (1376224250, 1376224250))
os.utime(os.path.join(ref_dir, '0', 'file2'), \
         (1376174351, 1376174351))
os.utime(os.path.join(ref_dir, '0', 'file3'), \
         (1376224452, 1376224452))
os.utime(os.path.join(ref_dir, '0', 'file3'), \
         (1376224553, 1376224553))
os.utime(os.path.join(ref_dir, '0', 'dir1'), \
         (1376224654, 1376224654))
os.utime(os.path.join(ref_dir, '0', 'dir2'), \
         (1376224755, 1376224755))
os.utime(os.path.join(ref_dir, '0', 'dir3'), \
         (1376224856, 1376224856))
os.utime(os.path.join(ref_dir, '0', 'dir4'), \
         (1376224950, 1376224950))
os.utime(os.path.join(ref_dir, '0', 'dir2', 'dir21'), \
         (1376225050, 1376225050))
os.utime(os.path.join(ref_dir, '0', 'dir2', 'dir22'), \
         (1376225150, 1376225150))
os.utime(os.path.join(ref_dir, '0', 'dir2', 'file21'), \
         (1376215250, 1376215250))
os.utime(os.path.join(ref_dir, '0', 'dir2', 'file22'), \
         (1376225350, 1376225350))
os.utime(os.path.join(ref_dir, '0', 'dir2', 'file23'), \
         (1376185450, 1376185450))
os.utime(os.path.join(ref_dir, '0', 'dir4', 'dir41'), \
         (1376225550, 1376225550))
os.utime(os.path.join(ref_dir, '0', 'dir4', 'fileA'), \
         (1376195650, 1376195650))
os.utime(os.path.join(ref_dir, '0', 'dir4', 'fileB'), \
         (1376165750, 1376165750))
os.utime(os.path.join(ref_dir, '0', 'dir4', 'dir41', 'fileA1'), \
         (1376225850, 1376225850))

# Test 1
print "Create a new backup"
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
if os.path.exists(dir_to_backup):
    rm_dir_content(dir_to_backup)
else:
    os.makedirs(dir_to_backup)
copytree(os.path.join(ref_dir, '0'), dir_to_backup)

fs_photo = take_fs_photo(srce_dir)
# Test
my_backup = BckTarGroup('Test', srce_dir, dest_dir, work_dir, password)
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
print "Nb elements: " + str(len(bck_submembers))
if result:
    print 'Test 1: OK\n\n'
else:
    print 'Test 1: KO'
    sys.exit(1)

time.sleep(1)
# Test 2
print "Read an existing backup"
# Preparation
print '-'*5 + ' Test 2 ' + '-'*5
del my_backup
fs_photo = take_fs_photo(srce_dir)
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
print "Nb elements: " + str(len(bck_submembers2))
if result:
    print 'Test 2: OK\n\n'
else:
    print 'Test 2: KO'
    sys.exit(2)   

time.sleep(1)
# Test 3
print "Update an existing backup with the last member not full"
# Preparation
print '-'*5 + ' Test 3 ' + '-'*5
os.utime(os.path.join(srce_dir, 'dir2', 'file21'), None)
fs_photo3 = take_fs_photo(srce_dir)
# Test
#print backup_name
#my_backup = BckTarGroup(backup_name, srce_dir, dest_dir, work_dir, password)
my_backup3 = my_backup.update()
my_backup3.print_members()
bck_submembers = my_backup.getsubmembers()
bck_submembers3 = my_backup3.getsubmembers()
# Result
print "Nb elements: " + str(len(bck_submembers3))
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
print "Update an existing backup"
print "but not change has been done on the file system"
# Preparation
print '-'*5 + ' Test 4 ' + '-'*5
# Test
#print backup_name
#my_backup = BckTarGroup(backup_name, srce_dir, dest_dir, work_dir, password)
my_backup4 = my_backup3.update()
bck_submembers4 = my_backup4.getsubmembers()
my_backup4.print_members()
# Result
print "Nb elements: " + str(len(bck_submembers4))
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
print "Update an existing backup where all members of a tar has been updated"
# Preparation
print '-'*5 + ' Test 5 ' + '-'*5
os.utime(os.path.join(srce_dir, 'file4'), None)
os.utime(os.path.join(srce_dir, 'dir4', 'fileA'), None)
fs_photo5 = take_fs_photo(srce_dir)
# Test
#print backup_name
#my_backup = BckTarGroup(backup_name, srce_dir, dest_dir, work_dir, password)
my_backup5 = my_backup4.update()
bck_submembers5 = my_backup5.getsubmembers()
my_backup5.print_members()
backup5_name = my_backup5.name
# Result
result = True
if bck_submembers5 != fs_photo5:
    logging.debug('Backup does not reflect the file system')
    result = False
elif my_backup5.members[1].index == 2:
    logging.debug('Tar 2 is not empty')
    result = False
# Output
print "Nb elements: " + str(len(bck_submembers5))
if result:
    print 'Test 5: OK\n\n'
else:
    print 'Test 5: KO'
    sys.exit(3)   

time.sleep(1)
# Test 6
print "Restore last backup"
# Preparation
print '-'*5 + ' Test 6 ' + '-'*5
if os.path.exists(extract_dir):
    rm_dir_content(extract_dir)
else:
    os.makedirs(extract_dir)
fs_photo6 = take_fs_photo(srce_dir)
# Test
print backup5_name
my_backup6 = BckTarGroup(backup5_name, srce_dir, dest_dir, work_dir, password)
my_backup6.extract(extract_dir)
# Result
my_backup6.print_members()
fs_extract = take_fs_photo(extract_dir)
bck_submembers6 = my_backup6.getsubmembers()
result = True
dir_comp = filecmp.dircmp(srce_dir, extract_dir)
dir_comp.report_full_closure()
if dir_comp.left_only or dir_comp.right_only:
    logging.debug('Restore backup does not reflect the file system')
    result = False
# Output
print "Nb elements: " + str(len(bck_submembers6))
if result:
    print 'Test 6: OK\n\n'
else:
    print 'Test 6: KO'
    sys.exit(3)   

time.sleep(1)
# Test 7
print "List existing backup"
# Preparation
print '-'*5 + ' Test 7 ' + '-'*5
# Test
bck_list = get_bcktargroups('Test', dest_dir)
# Output
print bck_list
last_bck = bck_list[-1]
print last_bck
