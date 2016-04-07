#!/usr/bin/env python
# -*- coding: utf-8 -*- 
__author__="EIXXIE"

from builtins import object
#from crypt import crypt
from string import ascii_letters, digits
from random import choice
import subprocess
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class UserExists(Exception):
    def __str__(self):
        return "User already exists"


class UserNotExists(Exception):
    def __str__(self):
        return "User not exists"


class UnknownEncryptionMode(Exception):
    def __init__(self, mode):
        self.mode = mode
    def __str__(self):
        return "Encryption Mode %s is unknown/unsupported" % self.mode


class HtpasswdUser(object):
    def __init__(self, userdb, mode='md5'):
        self.encryption_mode = mode
        self.userdb = userdb
        self.initial_users = OrderedDict()
        self.new_users = OrderedDict()

    def __enter__(self):
        with open(self.userdb, "r") as users:
            for i in users:
                user, password = i.split(":", 1)
                self.initial_users[user] = password
        self.new_users = self.initial_users.copy()
        return self

    def __exit__(self, type, value, traceback):
        if self.new_users == self.initial_users:
            return
        with open(self.userdb, "w") as userdb:
            for user in self.new_users:
                userdb.write("%s:%s" % (user, self.new_users[user]))

    def __contains__(self, user):
        return user in self.users

    @property
    def users(self):
        #返回用户的key
        return list(self.new_users.keys())

    def add(self, user, password):
        #添加用户
        if self.__contains__(user):
            self.change_password(user,password)
        self.new_users[user] = str(self._encrypt_password(password)) + "\n"

    def pop(self, user):
        #删除用户
        if not self.__contains__(user):
            pass
        self.new_users.pop(user)

    def change_password(self, user, password):
        #修改密码
        if not self.__contains__(user):
            self.add(user,password)
        self.new_users[user] = str(self._encrypt_password(password)) + "\n"

    def _encrypt_password(self, password):
        #
        if self.encryption_mode.lower() == 'crypt':
            return self._crypt_password(password)
        elif self.encryption_mode.lower() == 'md5':
            return self._md5_password(password)
        else:
            raise UnknownEncryptionMode(self.encryption_mode)

    def _crypt_password(self, password):
        """ Crypts password """

        def salt():
            """ Generates some salt """
            symbols = ascii_letters + digits
            return choice(symbols) + choice(symbols)

        #return crypt(password, salt())

    def _md5_password(self, password):
        """ Crypts password using openssl binary and MD5 encryption """
        return subprocess.check_output(['openssl', 'passwd', '-apr1', password]).decode('utf-8').strip()
