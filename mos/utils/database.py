#!/usr/bin/env python
# -*- coding: utf-8 -*- 
__author__="EIXXIE"

from sqlalchemy import create_engine,func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import json
from config import SQLALCHEMY_DATABASE_URI
#from config import SQLALCHEMY_MIGRATE_REPO
from mos import db

engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)

def aviable_groups_for_user(userid):
    groups=[]
    conn = engine.connect()
    sql = 'select groups.id as groupid,groupname FROM groups CROSS JOIN uig where groups.id = uig.group_id and uig.user_id = \'' + \
            str(userid) + '\' ' + 'order by groupname'
    print(sql)
    rs = conn.execute(sql)
    for r in rs:
        print(r)
        groups.append(r)
        #groups.append([r.groupid,r.groupname])
        return groups
    
def get_record_nums():
    user_all_nums = db_session.query(User).count()
    user_active_nums = db_session.query(User).filter(User.is_active=='1').count()
    group_all_nums = db_session.query(Group).count()
    group_active_nums = db_session.query(Group).filter(Group.is_active=='1').count() 
    repo_all_nums = db_session.query(Repo).count()
    repo_active_nums = db_session.query(Repo).filter(Repo.is_active=='1').count()    
    authitem_all_nums = db_session.query(AuthItem).count()
    datas={'user_all_nums':user_all_nums, 'user_active_nums':user_active_nums,\
           'group_all_nums':group_all_nums,'group_active_nums':group_active_nums,\
           'repo_all_nums':repo_all_nums,'repo_active_nums':repo_active_nums,\
           'authitem_all_nums':authitem_all_nums} 
    return datas

def SetData(type,para):
    conn = engine.connect()
    if type=='authitem':
        sql = 'select repos.id FROM auth_items CROSS JOIN repos where repos.reponame = \'' + para[0] +'\' '
        print(sql)
        rs = conn.execute(sql)
        for r in rs:
            repo_id = r[0]
        sql = 'insert into auth_items(\'repo_id\',\'authitem\') values(\'' + str(repo_id) +'\',' +'\'' + para[1] + '\')'
        print(sql)
        rs = conn.execute(sql)

#获得包含用户名和密码的用户数据
def get_user_passwd(reponame):
    users=[]
    conn = engine.connect()
    if reponame=='irepresentalltherepos':
        sql = 'select username,password from users'
    else:
        sql = 'select username,password from users cross join auth_users,repos,auth_items where auth_users.user_id=users.id and auth_users.authitem_id = auth_items.id and auth_items.repo_id = repos.id and repos.reponame = \'' + reponame +'\' order by reponame,authitem,username,authtype'
    rs = conn.execute(sql)
    for r in rs:
        users.append({'username':r.username,'password':r.password})
    #print(users)
    return users
    
#获取特定格式的数据        
def GetData(type,para):
    conn = engine.connect()
    #单项配置项数据
    if type == 'authitemid':
        authitem=[]
        sql = 'select auth_items.id as id,reponame,authitem FROM auth_items CROSS JOIN repos where auth_items.repo_id = repos.id \
        and repos.reponame = \'' + para[0] +'\' and auth_items.authitem = \'' + para[1] + '\' order by reponame,authitem'
        #print(sql)
        rs = conn.execute(sql)
        for r in rs:
            #print(r)
            authitem.append(r)
            return r[0]
    elif type == 'authiteminfo':
        authitem=[]
        sql = 'select reponame,authitem FROM auth_items CROSS JOIN repos where auth_items.repo_id = repos.id \
        and auth_items.id = \'' + para[0] + '\' order by reponame'
        #print(sql)
        rs = conn.execute(sql)
        for r in rs:
            #print(r)
            authitem.append(r)
            return authitem
    elif type == 'authitems':
        authitems=[]
        if para=='all':
            sql = 'select auth_items.id as id,reponame,authitem FROM auth_items CROSS JOIN repos where auth_items.repo_id = repos.id order by reponame,authitem'            
        else:
            sql = 'select auth_items.id as id,reponame,authitem FROM auth_items CROSS JOIN repos where auth_items.repo_id = repos.id and \
            repos.reponame like \'%' + para + '%\' order by reponame,authitem'
        #print(sql)
        rs = conn.execute(sql)
        for r in rs:
            #print(r)
            authitems.append(r)
        #print(authitems)
        return authitems
    elif type == 'users-json':
        users=[]
        if para=='all':
            sql = 'select id,fullname,username FROM users order by username'            
        else:
            pass
        #print(sql)
        rs = conn.execute(sql)
        for r in rs:
            #print(r)
            users.append({'id':r.id,'name':r.fullname + ' (' + r.username + ' )'})
        json_users = json.dumps(users)
        #print(users)
        #print(json_users)
        return json_users
    elif type == 'groups-json':
            groups=[]
            if para=='all':
                sql = 'select id,groupname FROM groups order by groupname'
            else:
                pass
            rs = conn.execute(sql)
            for r in rs:
                #print(r)
                groups.append({'id':r.id,'name':r.groupname})
            json_groups = json.dumps(groups)
            #print(groups)
            #print(json_groups)
            return json_groups 
    elif type == 'repos-json':
            repos=[]
            if para=='all':
                sql = 'select id,reponame FROM repos order by reponame'
            else:
                pass
            rs = conn.execute(sql)
            for r in rs:
                #print(r)
                repos.append({'id':r.id,'name':r.reponame})
            json_repos = json.dumps(repos)
            #print(repos)
            #print(json_repos)
            return json_repos   
    elif type == 'repos':
            repos=[]
            if para=='all':
                sql = 'select id,reponame FROM repos order by reponame'
            else:
                pass
            rs = conn.execute(sql)
            for r in rs:
                #print(r)
                repos.append(r.reponame)
            return repos 

#获取配置库相关的组包含用户的信息
def get_user_groups(reponame):
    user_groups=[]
    conn = engine.connect()
    if reponame=='irepresentalltherepos':
        sql = 'select groupname,username from auth_groups cross join uig,groups,users,repos,auth_items where auth_groups.group_id=groups.id and auth_groups.authitem_id = auth_items.id and auth_items.repo_id = repos.id and uig.user_id = users.id and uig.group_id = groups.id order by reponame,username'
    else:
        sql = 'select groupname,username from auth_groups cross join uig,groups,users,repos,auth_items where auth_groups.group_id=groups.id and auth_groups.authitem_id = auth_items.id and auth_items.repo_id = repos.id and uig.user_id = users.id and uig.group_id = groups.id and repos.reponame = \'' + reponame +'\' order by reponame,username'
    rs = conn.execute(sql)
    groups = set([])
    for r in rs:
        groups.add(r.groupname)
    names = locals()
    for group in groups:
        names['%s' % group] = {'groupname':group,'users':''}
        names['users_%s' % group] = ''
        rs = conn.execute(sql)
        for r in rs:
            if r.groupname == group:
                names['users_%s' % group]=names['users_%s' % group]+','+r.username
        names['%s' % group]['users']=list(set((names['users_%s' % group].lstrip(',')).split(',')))
        names['%s' % group]['users'] = ','.join(names['%s' % group]['users'])
        user_groups.append(names['%s' % group])
    return user_groups

#获取用户及组的权限认证信息
def get_auths(type,reponame):
    auths=[]
    conn = engine.connect()
    if type=='user':
        if reponame=='irepresentalltherepos':
            sql = 'select reponame,authitem,username,authtype from auth_users cross join users,repos,auth_items where auth_users.user_id=users.id and auth_users.authitem_id = auth_items.id and auth_items.repo_id = repos.id order by reponame,authitem,username,authtype'
        else:
            sql = 'select reponame,authitem,username,authtype from auth_users cross join users,repos,auth_items where auth_users.user_id=users.id and auth_users.authitem_id = auth_items.id and auth_items.repo_id = repos.id and repos.reponame = \'' + reponame +'\' order by reponame,authitem,username,authtype'
        rs = conn.execute(sql)
        for r in rs:
            #print(r)
            auths.append({'reponame':r.reponame,'authitem':r.authitem,'username':r.username,'authtype':r.authtype}) 
    elif type=='group':
        if reponame=='irepresentalltherepos':
            sql = 'select reponame,authitem,groupname,authtype from auth_groups cross join groups,repos,auth_items where auth_groups.group_id=groups.id and auth_groups.authitem_id = auth_items.id and auth_items.repo_id = repos.id order by reponame,authitem,groupname,authtype'
        else:
            sql = 'select reponame,authitem,groupname,authtype from auth_groups cross join groups,repos,auth_items where auth_groups.group_id=groups.id and auth_groups.authitem_id = auth_items.id and auth_items.repo_id = repos.id and repos.reponame = \'' + reponame +'\' order by reponame,authitem,groupname,authtype'    
        rs = conn.execute(sql)
        for r in rs:
            #print(r)
            auths.append({'reponame':r.reponame,'authitem':r.authitem,'groupname':r.groupname,'authtype':r.authtype}) 
    return auths
    
def get_groups():
    conn = engine.connect()
    sql = 'select id,groupname from groups order by groupname'
    rs = conn.execute(sql)

#检查配置项是否已经存在    
def is_data_exist(type,para):
    conn = engine.connect()
    if type == 'authitem':
        authitem=[]
        sql = 'select repo_id,authitem FROM auth_items where auth_items.repo_id = \'' + para[0] \
            +'\' and auth_items.authitem = \'' + para[1] + '\' order by repo_id'
        #print(sql)
        rs = conn.execute(sql)
        for r in rs:
            #print(r)
            authitem.append(r)
        if len(authitem)==0:
            return False
        else:
            return True
    else:
        return '参数错误'
    


class DBMaster(object):
    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    def save(self):
        db_session.add(self)
        #try:
        db_session.commit()
        #except:
            #db_session.rollback()
        return self

    def delete(self):
        db_session.delete(self)
        db_session.commit()
        return self


