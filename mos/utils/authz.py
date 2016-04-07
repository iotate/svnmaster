#!/usr/bin/env python
# -*- coding: utf-8 -*- 
__author__="EIXXIE"

import os,os.path,time, platform,re,configparser,codecs,shutil,subprocess
from mos.utils.functions import get_now_time2,Info2RW
from mos.utils.database import get_auths,get_user_groups,get_user_passwd,GetData
from mos.utils.htpasswd import HtpasswdUser
from config import REPOS_DIRS,REPOS_BASE_URL,SVN_HTTPD_AUTHZ,SVN_HTTPD_USERS,SVN_AUTH_MODE

#创建UTF-8编码的文件，因为authz文件中可能包含中文
def create_new_file(path,code):
    f = codecs.open(path,'a',code)
    #f.write(u'中文')
    f.close()

#检查文件是否存在
def check_file_exists(filepath):
    #如果文件已经存在，则重命名之
    if os.path.isfile(filepath):
        os.rename(filepath,filepath + '.' + get_now_time2())
    create_new_file(filepath, 'utf-8')

#httpd方式下，新增用户
def add_httpd_user(username,password):
    if os.path.isfile(SVN_HTTPD_USERS):
        shutil.copyfile(SVN_HTTPD_USERS,SVN_HTTPD_USERS + '.' + get_now_time2())
    else:
        create_new_file(SVN_HTTPD_USERS, 'utf-8')
    subprocess.check_output(['htpasswd', '-b',SVN_HTTPD_USERS,username,password]).decode('utf-8').strip()
    #with HtpasswdUser(SVN_HTTPD_USERS) as userdb:
    #    userdb.add(username, password) 

#httpd方式下，删除用户
def del_httpd_user(username):
    if os.path.isfile(SVN_HTTPD_USERS):
        shutil.copyfile(SVN_HTTPD_USERS,SVN_HTTPD_USERS + '.' + get_now_time2())
    else:
        create_new_file(SVN_HTTPD_USERS, 'utf-8')
    subprocess.check_output(['htpasswd', '-D',SVN_HTTPD_USERS,username]).decode('utf-8').strip()    
    #with HtpasswdUser(SVN_HTTPD_USERS) as userdb:
    #    userdb.pop(username) 

#httpd方式下，修改用户密码
def repwd_httpd_user(username,password):
    if os.path.isfile(SVN_HTTPD_USERS):
        shutil.copyfile(SVN_HTTPD_USERS,SVN_HTTPD_USERS + '.' + get_now_time2())
    else:
        create_new_file(SVN_HTTPD_USERS, 'utf-8')
    subprocess.check_output(['htpasswd', '-D',SVN_HTTPD_USERS,username]).decode('utf-8').strip()
    subprocess.check_output(['htpasswd', '-b',SVN_HTTPD_USERS,username,password]).decode('utf-8').strip()
    #with HtpasswdUser(SVN_HTTPD_USERS) as userdb:
    #    userdb.change_password(username, password) 

#生成authz文件，考虑多库共用一个authz和每个库各一个authz文件的情形
def gen_single_authz(reponame):
    if reponame == 'irepresentalltherepos':
        auth_file = SVN_HTTPD_AUTHZ
    else:
        auth_file = os.path.join(REPOS_DIRS,reponame,'conf\\authz')
    check_file_exists(auth_file)
    #对配置文件进行写入
    cf = configparser.ConfigParser()
    cf.read(auth_file)
    user_groups = get_user_groups(reponame)
    user_auths = get_auths('user',reponame)
    group_auths = get_auths('group',reponame)
    #写入组信息
    if not cf.has_section('groups'):
        cf.add_section('groups')
    for user_group in user_groups:
        cf.set('groups',user_group['groupname'],user_group['users'])
    #多库共用authz文件的写入方式为[reponame:authitem]
    if reponame == 'irepresentalltherepos':
        #写入用户权限
        for auth in user_auths:
            #print(auth)
            if not cf.has_section(auth['reponame'] + ':' + auth['authitem']):
                cf.add_section(auth['reponame'] + ':' + auth['authitem'])
            cf.set(auth['reponame'] + ':' + auth['authitem'],auth['username'],Info2RW(auth['authtype']))
        #写入组权限
        for auth in group_auths:
            #print(auth)
            if not cf.has_section(auth['reponame'] + ':' + auth['authitem']):
                cf.add_section(auth['reponame'] + ':' + auth['authitem'])
            cf.set(auth['reponame'] + ':' + auth['authitem'],'@'+auth['groupname'],Info2RW(auth['authtype'])) 
    #单库authz文件的写入方式为[authitem]
    else:
        #写入用户权限
        for auth in user_auths:
            #print(auth)
            if not cf.has_section(auth['authitem']):
                cf.add_section(auth['authitem'])
            cf.set(auth['authitem'],auth['username'],Info2RW(auth['authtype']))
        #写入组权限
        for auth in group_auths:
            #print(auth)
            if not cf.has_section(auth['authitem']):
                cf.add_section(+ auth['authitem'])
            cf.set(auth['authitem'],'@'+auth['groupname'],Info2RW(auth['authtype']))         
    cf.write(open(auth_file,"w"))

    

#生成httpd服务方式下的用户密码文件：htpasswd文件
def gen_httpd_users():
    check_file_exists(SVN_HTTPD_USERS)
    users = get_user_passwd('irepresentalltherepos')
    for user in users:
        #subprocess.check_output(['htpasswd', '-D',SVN_HTTPD_USERS,user['username']]).decode('utf-8').strip()
        subprocess.check_output(['htpasswd', '-b',SVN_HTTPD_USERS,user['username'],user['password']]).decode('utf-8').strip()    
    #with HtpasswdUser(SVN_HTTPD_USERS) as userdb:
    #    for user in users:
    #        userdb.add(user['username'], user['password'])

#生成httpd认证方式下的authz文件            
def gen_httpd_authzs():
    #对配置文件进行写入
    gen_single_authz('irepresentalltherepos')
    
#生成svnserver认证方式下的authz文件，每个库有一个文件    
def gen_svnserver_authzs():
    repos = GetData('repos','all')
    for repo in repos:
        gen_single_authz(repo)

#为单个库生成svnserver认证方式下的user文件
def gen_single_svn_server_users(reponame):
    users_file = os.path.join(REPOS_DIRS,reponame,'conf\\passwd')
    check_file_exists(users_file) 
    users = get_user_passwd(reponame)
    cf = configparser.ConfigParser()
    cf.read(users_file) 
    #写入section信息
    if not cf.has_section('users'):
        cf.add_section('users')
    for user in users:
        cf.set('users',user['username'],user['password'])
    cf.write(open(users_file,"w"))

#为所有库生成svnserver认证方式下的user文件，每个库一个文件
def gen_svnserver_users():
    repos = GetData('repos','all')
    for repo in repos:
        gen_single_svn_server_users(repo)
        
#刷新所有用户和权限文件
def refresh_all_users_auths():
    if SVN_AUTH_MODE == 'httpd':
        gen_httpd_users()
        gen_httpd_authzs()
    elif SVN_AUTH_MODE == 'svnserver':
        gen_svnserver_users()
        gen_svnserver_authzs()

        