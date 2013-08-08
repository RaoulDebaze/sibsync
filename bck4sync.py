#! /usr/bin/env python

# TODO 001: Manage symlink
# DONE 002: Add empty directory
# TODO 003: Manage an directories exceptions list
# TODO 004: Exclude too big files

# Need Python >= 2.5
import datetime
import fnmatch
import getpass
import logging
import os
#import random
import re
import shutil
import string
import struct
import socket
import tarfile
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Hash import SHA256

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

# Functions to encrypt / decrypt files
# http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
# import os, random, struct
# from Crypto.Cipher import AES
#
# Install on RHEL:
#   yum install python-devel.x86_64
#   cd pycrypto-2.6
#   python setup.py build
#   python setup.py install
def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)
        
class BckTarFile:
    def __init__(self, *args):
        #__init__(name, dest_dir, work_dir, max_size)
        if len(args) == 5:
            self.name = args[0]
            self.dest_dir = args[1]
            self.work_dir = args[2]
            self.max_size = args[3]
            self.key = args[4]
            (self.prefix, index, self.datetime) = \
                    string.split(self.name, '-')
            self.index = int(index)
        #__init__(self, prefix, index, datetime, dest_dir, work_dir, max_size):
        elif len(args) == 7:
            self.prefix = args[0]
            self.index = args[1]
            self.datetime = args[2]
            self.dest_dir = args[3]
            self.work_dir = args[4]
            self.max_size = args[5]
            self.key = args[6]
            self.name = self.prefix + '-' \
                    + str(self.index).zfill(10) + '-' \
                    + self.datetime
        else:
            raise NameError('No constructor available')

        self.clear_suffix = '.tgz'
        self.encrypted_suffix = '.enc'
        self.dest_fullname = os.path.join(self.dest_dir, \
                self.name + self.encrypted_suffix)
        self.work_fullname = os.path.join(self.work_dir, \
                self.name + self.clear_suffix)
        self.members = []
        self.tarfile = None
        
    def open(self, mode):
        logging.debug("Open " + self.name + " in mode " + mode)
        if mode == 'w':
            self.mode = 'w:gz'
        else:
            self.mode ='r:gz'
            decrypt_file(self.key, self.dest_fullname, self.work_fullname)
        self.tarfile = tarfile.open(self.work_fullname, mode)

    def close(self):
        # Close tar file
        logging.debug("Close " + self.name)
        self.tarfile.close()
        self.tarfile = None
        # Move tar file from work to destination dir
        if self.mode == 'w:gz':
            # File is in write mode
            encrypt_file(self.key, self.work_fullname, self.dest_fullname)
        os.remove(self.work_fullname)
    
    def extract(self, extract_dir):
        logging.debug('Extract ' + self.name)
        
        self.open('r')
        self.tarfile.extractall(path = extract_dir)
        self.close()
        
    def is_full(self):
        if os.path.isfile(self.work_fullname):
            return (os.stat(self.work_fullname).st_size > self.max_size)
        elif os.path.isfile(self.dest_fullname):
            return (os.stat(self.dest_fullname).st_size > self.max_size)
        else:
            return false
    
    def add(self, file_name):
        self.tarfile.add(file_name, recursive=False)
        if os.path.isdir(file_name):
            file_size = 0
        else:
            file_size = os.stat(file_name).st_size
        self.members.append({'path': os.path.normpath(file_name),
                'mtime': int(os.stat(file_name).st_mtime),
                'size': file_size})


    def getmembers(self):
        logging.debug('Read members from ' + self.name)

        if not self.members:
            self.members = []
            # Tarfile has never been opened
            # => Open in 'r' mode to read tarfile members
            if not self.tarfile:
                self.open('r')
                tarfile_members = self.tarfile.getmembers()
                self.close()
            for member in tarfile_members:
                self.members.append({\
                        'path': os.path.normpath(member.name),
                        'mtime': int(member.mtime),
                        'size': member.size})
        return self.members
            
class BckTarGroup:
    """All files for a complete backup"""
    
    def __init__(self, *args):
        self.suffix = 'bck4sync'
        test_name = args[0].rstrip('.' + self.suffix)
        # Initialize from an exisiting ctrl file
        # Test if first argument looks like a backup name
        print args[0]
        print len(args[0])
        print len(test_name)
        print test_name
        if re.search('-[2-9]\d{3}[0-1]\d[0-3]\d[0-2]\d[0-5]\d[0-5]\d$', \
                test_name):
            logging.debug('Construct BckTarGroup by name')
            self.name = test_name
            self.srce_dir = args[1]
            self.dest_dir = args[2]
            self.work_dir = args[3]
            self.password = args[4]
            (self.prefix, self.datetime) = \
                    string.split(self.name, '-')
        else:
            logging.debug('Construct BckTarGroup from a prefix')
            self.prefix = args[0]
            self.srce_dir = args[1]
            self.dest_dir = args[2]
            self.work_dir = args[3]
            self.password = args[4]
            self.datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            self.name = self.prefix + '-' + self.datetime
            
        self.max_members_size = (5*1024*1024)
        self.key = SHA256.new(self.password).digest()
        self.bcktar_members = []
        self.members = []
    
    def _get_srce_files(self):
        logging.debug('List and sort files in ' + self.srce_dir)
 
        files = []
        os.chdir(self.srce_dir)
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

    def _read_members(self):
        logging.debug('Read bcktar members from ' + self.name)
        
        # List bcktar files
        self.open('r')
        self.members = []
        for ctrl_line in self.ctrl_file:
            bcktar_file = BckTarFile(ctrl_line.rstrip('\n'), \
                    self.dest_dir, self.work_dir, \
                    self.max_members_size, self.key)
            self.members.append(bcktar_file)
        self.close()

    def open(self, mode):
        logging.debug('Open backup ' + self.name + ' in mode ' + mode)
        self.mode = mode
        if mode == 'w':
            self.bcktar_members = []
            self.members = []
            self.fullname = os.path.join(self.dest_dir,
                    self.name + '.inProgress')
        elif mode == 'r':
            self.fullname = os.path.join(self.dest_dir,
                    self.name + '.' + self.suffix)
        self.ctrl_file = open(self.fullname, self.mode)

    def close(self):
        logging.debug('Close backup')
        self.ctrl_file.close()
        completed_fullname = os.path.join(self.dest_dir,
                self.name + '.' + self.suffix)
        os.rename(self.fullname, completed_fullname)
        self.fullname = completed_fullname

    def _append_bcktar(self, bcktar_file = None):
        if not bcktar_file:
            # Create an empty bcktar_member
            index = len(self.bcktar_members) + 1
            bcktar_file = BckTarFile(\
                    self.prefix, index, \
                    self.datetime, self.dest_dir, self.work_dir, \
                    self.max_members_size, \
                    self.key)
        self.bcktar_members.append(bcktar_file)
        self.ctrl_file.write(self.bcktar_members[-1].name + '\n')
                        
    def _append_files(self, files):
        # Open a new bcktar to append files to bckgroup
        self._append_bcktar()
        self.bcktar_members[-1].open('w')
        
        sorted_files = sorted(files, key=lambda mtime: mtime['mtime'])
        for file in sorted_files:
            # Open a new bcktar file if
            # last tar file is full
            if self.bcktar_members[-1].is_full():
                self.bcktar_members[-1].close()
                self._append_bcktar()
                self.bcktar_members[-1].open('w')

            self.bcktar_members[-1].add(file['path'])

        self.bcktar_members[-1].close()
            
    def is_complete(self):
        is_complete = True
        if not self.bcktar_members:
            self._set_bcktar_members()
        for bcktar_file in self.bcktar_members:
            if not os.path.isfile(bcktar_file.dest_fullname):
                is_complete = False
                break
                
        return is_complete
        
    def create(self):
        logging.debug('Create a new full backup of ' + self.srce_dir)
 
        self.open('w')

        srce_files = self._get_srce_files()
        self._append_files(srce_files)

        self.close()
 
    def update(self):
        logging.debug('Update ' + self.name)

        # Create a new backup with now time
        updated_bck = BckTarGroup(\
                self.prefix, \
                self.srce_dir, self.dest_dir, self.work_dir, \
                self.password, \
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        updated_bck.open('w')
        
        if not self.members:
            self._read_members()

        # Get files list on the file system
        srce_files=self._get_srce_files()

        # Compare tar members with files on file system
        next_submembers = self.getsubmembers()
        new_members = []
        # Loop over each member (=each tar files)
        for member in self.members:
            new_submembers = []
            ori_submembers = member.getmembers()
            # Remove files from current tar of next list
            next_submembers = \
                [ submember for submember in next_submembers \
                    if submember not in ori_submembers ]
            while srce_files \
                    and (srce_files[0]['mtime'] <= \
                    ori_submembers[-1]['mtime']):
                # Break in current file is in one of the next tars
                if srce_files[0]['path'] in \
                        [i['path'] for i in next_submembers]:
                    break
                new_submembers.append(srce_files.pop(0))
                # Break if the file we had is the last from members in tar
                # Necessary for last members_in_tar
                if new_submembers[-1]['path'] == \
                        ori_submembers[-1]['path']:
                    break
            # Cannot work !
            if ori_submembers == new_submembers:
                new_members._append_bcktar(member)
            elif new_submembers:
                new_members._append_bcktar()

        if (self.members == new_members) and not srce_files:
            # The backup is up-to-date
            logging.debug(self.name + ' is up-to-date')
        else:
            logging.debug(self.name + ' is not update')

        # Loop over all bcktar except last one, which will be treated separetly
        for bcktar_index in range(len(self.bcktar_members) - 1):
            if self.members[bcktar_index] == new_members[bcktar_index]:
                # tar is up-to-date
                # => resuse it for new backup
                logging.debug('Add ' + \
                        self.bcktar_members[bcktar_index].name)
                updated_bck._append_bcktar(self.bcktar_members[bcktar_index])
            elif new_members[bcktar_index]:
                # At least one members has been updated or removed
                # And new tar will not be empty
                # => recreate a new tar
                updated_bck._append_bcktar()
                logging.debug('Write ' + updated_bck.bcktar_members[-1].name)
                updated_bck.bcktar_members[-1].open('w')
                for member in new_members[bcktar_index]:
                    updated_bck.bcktar_members[-1].add(member['path'])
                updated_bck.bcktar_members[-1].close()
            else:
                # All file from tar has been updated
                # => Add en empty element
                updated_bck.bcktar_members.append(None)

        # -1 because list start at 0 but BckTarFile at 1
        bcktar_index = len(self.bcktar_members) - 1
        # Treat the last BckTarFile
        if self.members[-1] == new_members[-1] \
                and (self.bcktar_members[-1].is_full() \
                or not srce_files) :
            # No update needed for last bcktar
            logging.debug('Add ' + self.bcktar_members[bcktar_index].name)
            logging.debug('Add ' + \
                    self.bcktar_members[-1].name)
            updated_bck._append_bcktar(self.bcktar_members[-1])
        else:
            # Update needed for last bcktar
            # => Add files from last member to remaining files
            # => New BckTarFile will be recreated during next step
            srce_files = new_members[-1] + srce_files

        # Apend new files
        if srce_files:
            logging.debug('Append remaining files')
            updated_bck._append_files(srce_files)
        
        updated_bck.close()
        
        return updated_bck

    def extract(self, extract_dir):
        if not self.members:
            self._set_members()

        for bcktar_file in self.bcktar_members:
            bcktar_file.extract(extract_dir)

    def getmembers(self):
        if not self.members:
            self._read_members()
        return self.members

    def getsubmembers(self):
        if not self.members:
            self._read_members()

        submembers = []
        for member in self.members:
            for submember in member.getmembers():
                submembers.append(submember)
        return submembers
                
    def print_members(self):
        if not self.members:
            self._read_members()

        for member in self.members:
            print member.name
            for submember in member.getmembers():
                mtime = datetime.datetime\
                        .fromtimestamp(int(submember['mtime']))\
                        .strftime('%Y-%m-%d %H:%M:%S')
                print '    %s %10s %s' % ( \
                        mtime, submember['size'], submember['path'])
