#!/usr/bin/env python
# -*- coding: utf-8 -*- 
__author__="EIXXIE"

#将MOS文件夹添加到系统环境变量
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from sqlalchemy import orm,or_, and_, desc
from sqlalchemy import Table, Column, Integer, String
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask.ext.login import UserMixin
from functools import partial
from mos.utils.database import Base,engine,db_session
from mos.utils.functions import get_now_time,Bool2Info
from mos import db
#

#用户表定义
class User(UserMixin,Base):
    __tablename__ = 'users'
    id = db.Column('id', Integer, primary_key=True)
    fullname = db.Column('fullname', String(50))
    username = db.Column('username', String(20), unique=True)
    password = db.Column('password', String(20))
    email = db.Column('email', String(30))
    comments = db.Column('comments', String(200))
    is_admin = db.Column('is_admin', String(2))
    is_active = db.Column('is_active', String(2))
    lasttime = db.Column('lasttime', String(30))

    #判断该用户是否属于某个组
    def isingroup(self,group_id):
        result =[]
        conn = engine.connect()
        sql = 'select * from uig where group_id = \'' + str(group_id) + '\' and user_id=\'' + str(self.id) +'\''
        rs = conn.execute(sql)
        for r in rs:
            result.append(r)
        if len(result)==0:
            return False
        else:
            return True
        
    #列出该用户所属的组的名称    
    def has_groups(self):
        groups =[]
        conn = engine.connect()
        sql = 'select groups.id as groupid,groupname FROM groups CROSS JOIN uig where groups.id = uig.group_id and uig.user_id = \'' + \
            str(self.id) + '\'' + 'order by groupname'
        rs = conn.execute(sql)
        for r in rs:
            groups.append([r.groupid,r.groupname])
        return groups

    #将用户加入某个组            
    def joingroup(self,group_id):
        if not self.isingroup(group_id):
            conn = engine.connect()
            sql = 'insert into uig(\'group_id\',\'user_id\',\'lasttime\') values(\'' + str(group_id) + '\',' + '\'' + str(self.id) +'\',' + '\'2012-03-31 20:58:40\')'
            rs = conn.execute(sql)
            return True
        else:
            return False
    
    #将用户从某个组中移除    
    def leavegroup(self,group_id):
        if self.isingroup(group_id):
            conn = engine.connect()
            sql = 'delete from uig where group_id = \'' + str(group_id) + '\' and user_id=\'' + str(self.id) +'\''
            rs = conn.execute(sql)
            return True
        else:
            return False

    #列出该用户所属的权限    
    def has_auths(self):
        userauths =[]
        conn = engine.connect()
        sql = 'select reponame,authitem,authtype from auth_users cross join users,repos,auth_items where auth_users.user_id=users.id and auth_users.authitem_id = auth_items.id and auth_items.repo_id = repos.id and users.id = \'' + str(self.id) +'\' order by reponame,authitem,authtype'
        rs = conn.execute(sql)
        for r in rs:
            userauths.append([' ',r.reponame,r.authitem,r.authtype])
        return userauths

    def __init__(self, fullname=None, username=None, password=None, email=None,comments=None,is_admin=0,is_active=1,lasttime=None):
        #self.id = id
        self.fullname = fullname
        self.username = username
        self.password = password
        self.email = email
        self.comments = comments
        self.is_admin = is_admin
        self.is_active = is_active
        self.lasttime = lasttime

        def is_authenticated(self):
            return True

        def is_active(self):
            return True

        def is_anonymous(self):
            return False

        def get_id(self):
            try:
                return unicode(self.id)  # python 2
            except NameError:
                return str(self.id)  # python 3
            
    #def groups(self):
    #    return db.session.query(Group).filter_by(id = self.id).all()
            
    def __repr__(self):
        return '%r,%r,%r,%r,%r,%r,%r,%r' % (self.fullname,self.username,self.password,self.email,self.comments,\
                                            self.is_admin,self.is_active,self.lasttime)


def getRepo(columns=None):
    r = Repo.query
    if columns:
        r = r.options(orm.load_only(*columns))
    return r

def getRepoFactory(columns=None):
    return partial(getRepo, columns=columns)

def getGroup(columns=None):
    r = Group.query
    if columns:
        r = r.options(orm.load_only(*columns))
    return r

def getGroupFactory(columns=None):
    return partial(getGroup, columns=columns)

#用户组表定义
class Group(Base):
    __tablename__ = 'groups'
    id = db.Column('id', Integer, primary_key=True)
    groupname = db.Column('groupname', String(20), unique=True)
    comments = db.Column('comments', String(200))
    status = db.Column('status', String(2))
    lasttime = db.Column('lasttime', String(30))
    
    #判断该组是否包含某个用户
    def ishavauser(self,user_id):
        result =[]
        conn = engine.connect()
        sql = 'select * from uig where user_id = \'' + str(user_id) + '\' and group_id=\'' + str(self.id) +'\''
        rs = conn.execute(sql)
        for r in rs:
            result.append(r)
        if len(result)==0:
            return False
        else:
            return True

    #列出该组所包含的用户的全名和登录名
    def has_users(self):
        users =[]
        conn = engine.connect()
        sql = 'select users.id as userid,fullname,username FROM users CROSS JOIN uig where users.id = uig.user_id and uig.group_id = \'' + \
            str(self.id) + '\'' + 'order by username'
        rs = conn.execute(sql)
        for r in rs:
            users.append([r.userid,r.fullname,r.username])
        return users
    
    #将某个用户加入该组            
    def joinuser(self,user_id):
        if not self.ishavauser(user_id):
            conn = engine.connect()
            sql = 'insert into uig(\'group_id\',\'user_id\',\'lasttime\') values(\'' + str(self.id) + '\',' + '\'' + str(user_id) +'\',' + '\'2012-03-31 20:58:40\')'
            rs = conn.execute(sql)
            return True
        else:
            return False    

    #列出该用户组所有的权限    
    def has_auths(self):
        groupauths =[]
        conn = engine.connect()
        sql = 'select groupname,reponame,authitem,authtype from auth_groups cross join groups,repos,auth_items where auth_groups.group_id=groups.id and auth_groups.authitem_id = auth_items.id and auth_items.repo_id = repos.id and groups.id = \'' + str(self.id) +'\' order by groupname,reponame,authitem,authtype'
        rs = conn.execute(sql)
        for r in rs:
            groupauths.append([r.groupname,r.reponame,r.authitem,r.authtype])
        return groupauths
    
    def __init__(self, groupname=None, comments=None,status=1,lasttime=None):
        #self.id = id
        self.groupname = groupname
        self.comments = comments
        self.status = status
        self.lasttime = lasttime

        def is_active(self):
            return True

        def get_id(self):
            try:
                return unicode(self.id)  # python 2
            except NameError:
                return str(self.id)  # python 3

    def __repr__(self):
        return '%r,%r,%r,%r' % (self.groupname,self.comments,self.status,self.lasttime)

    
#SVN库表定义
class Repo(Base):
    __tablename__ = 'repos'
    id = Column('id', Integer, primary_key=True)
    reponame = Column('reponame', String(50))
    comments = Column('comments', String(200))
    is_active = Column('is_active', String(2))
    lasttime = Column('lasttime', String(30))
    
    #列出该库所包含的配置项
    def has_Authitems(self):
        authitems=[]
        conn = engine.connect()
        sql = 'select authitem FROM repos CROSS JOIN auth_items where auth_items.repo_id = repos.id and repos.id = \'' + \
            str(self.id) + '\'' + 'order by authitem'
        rs = conn.execute(sql)
        for r in rs:
            authitems.append([r.authitem])
        return authitems

    def __init__(self, reponame=None,comments=None,is_active=1,lasttime=None,authitems=None):
        #self.id = id
        self.reponame = reponame
        self.comments = comments
        self.is_active = is_active
        self.lasttime = lasttime

        def get_id(self):
            try:
                return unicode(self.id)  # python 2
            except NameError:
                return str(self.id)  # python 3

    def __repr__(self):
        return '%r,%r,%r,%r,%r' % (self.reponame,self.comments,self.is_active,self.lasttime,self.authitems)
    
#配置项表定义
class AuthItem(Base):
    __tablename__ = 'auth_items'
    id = Column('id', Integer, primary_key=True)
    repo_id = Column('repo_id', String(50))
    authitem = Column('authitem', String(150))
    #repo_id = db.Column(db.Integer, db.ForeignKey('repos.id'))
    
     #判断是否包含某个用户的权限
    def is_hasuser(self,user_id):
        result = []
        conn = engine.connect()
        sql = 'select * from auth_users where authitem_id = \'' + str(self.id) + '\' and user_id= \'' + str(user_id) +'\''
        rs = conn.execute(sql)
        for r in rs:
            result.append(r)
        if len(result)==0:
            return False
        else:
            return True  
        
    #判断是否包含某个组的权限
    def is_hasgroup(self,group_id):
        result = []
        conn = engine.connect()
        sql = 'select * from auth_groups where authitem_id = \'' + str(self.id) + '\' and group_id= \'' + str(group_id) +'\''
        rs = conn.execute(sql)
        for r in rs:
            result.append(r)
        if len(result)==0:
            return False
        else:
            return True    
    #增加用户权限            
    def joinuser(self,user_id,authtype):
        conn = engine.connect()
        if not self.is_hasuser(user_id):
            sql = 'insert into auth_users(\'authitem_id\',\'user_id\',\'authtype\',\'lasttime\') values(\'' +\
                str(self.id) + '\',' + '\'' + str(user_id) +'\',' + '\'' + str(authtype) +'\',' + '\'2012-03-31 20:58:40\')'
        else:
            sql = 'update auth_users set authtype = \'' + str(authtype) +'\'' + ' where authitem_id = \'' + str(self.id) + '\' and user_id= \'' + str(user_id) +'\''
        rs = conn.execute(sql)


    #增加用户组权限            
    def joingroup(self,group_id,authtype):
        conn = engine.connect()
        if not self.is_hasgroup(group_id):
            sql = 'insert into auth_groups(\'authitem_id\',\'group_id\',\'authtype\',\'lasttime\') values(\'' + str(self.id) + '\',' + '\'' + str(group_id) +'\',' + '\'' + str(authtype) +'\',' + '\'2012-03-31 20:58:40\')'
            
        else:
            sql = 'update auth_groups set authtype = \'' + str(authtype) +'\'' + ' where authitem_id = \'' + str(self.id) + '\' and group_id= \'' + str(group_id) +'\''
        rs = conn.execute(sql)
        
    #将用户组权限移除
    def removeuser(self,user_id):
        conn = engine.connect()
        sql = 'delete from auth_users where user_id = \'' + str(user_id) + '\' and authitem_id=\'' + str(self.id) +'\''
        rs = conn.execute(sql)
        return True

    #将用户组权限移除
    def removegroup(self,group_id):
        conn = engine.connect()
        sql = 'delete from auth_groups where group_id = \'' + str(group_id) + '\' and authitem_id=\'' + str(self.id) +'\''
        rs = conn.execute(sql)
        return True


    #列出该配置项所包含的用户认证
    def has_authusers(self):
        authusers=[]
        conn = engine.connect()
        sql = 'select users.id as userid,fullname,username,authtype from auth_users cross join users,\
        repos,auth_items where auth_users.user_id=users.id and auth_users.authitem_id = auth_items.id and \
        auth_items.repo_id = repos.id and auth_items.id = \'' + str(self.id) + '\'' + 'order by username'
        rs = conn.execute(sql)
        for r in rs:
            authusers.append([r.userid,r.fullname,r.username,r.authtype])
        return authusers

    #列出该配置项所包含的用户组认证
    def has_authgroups(self):
        authgroups=[]
        conn = engine.connect()
        sql = 'select groups.id as groupid,groupname,authtype from auth_groups cross join groups,\
        repos,auth_items where auth_groups.group_id=groups.id and auth_groups.authitem_id = auth_items.id and \
        auth_items.repo_id = repos.id and auth_items.id = \'' + str(self.id) + '\'' + 'order by groupname'
        rs = conn.execute(sql)
        for r in rs:
            authgroups.append([r.groupid,r.groupname,r.authtype])
        return authgroups

    def __init__(self, repo_id=None,authitem=None):
        #self.id = id
        self.repo_id = repo_id
        self.authitem = authitem

        def get_id(self):
            try:
                return unicode(self.id)  # python 2
            except NameError:
                return str(self.id)  # python 3

    def __repr__(self):
        return '%r,%r' % (self.repo_id,self.authitem)

#权限表
class AuthPerm(Base):
    __tablename__ = 'authperms'
    id = Column('id', Integer, primary_key=True)
    authitem_id = Column('authitem_id', Integer)
    authtype = Column('authtype', String(10))
    authdata = Column('authdata', String(20))
    authperm = Column('authperm', String(5))
    comments = Column('comments', String(200))
    lasttime = Column('lasttime', String(30))

    def __init__(self, authitem_id=None, authtype=None, authdata=None, authperm=None,comments=None,lasttime=None):
        #self.id = id
        self.authitem_id = authitem_id
        self.authtype = authtype
        self.authdata = authdata
        self.authperm = authperm
        self.comments = comments
        self.lasttime = lasttime

        def get_id(self):
            try:
                return unicode(self.id)  # python 2
            except NameError:
                return str(self.id)  # python 3

    def __repr__(self):
        return '%r,%r,%r,%r,%r,%r' % (sself.authitem_id,self.authtype,self.authdata,self.authperm,self.comments,self.lasttime)