#!/usr/bin/env python
# -*- coding: utf-8 -*- 
__author__="EIXXIE"

import os
basedir = os.path.abspath(os.path.dirname(__file__))
#以上信息不要修改-------------以上信息不要修改-------------以上信息不要修改-------------以上信息不要修改-------------


#本系统使用的端口号
SERVER_PORT = 80

#SVN配置库存放的根目录，以\\结尾
REPOS_DIRS='d:\SVNMaster\Repos\\'
REPOS_BASE_URL='http://127.0.0.1/svn/'

#SVN认证相关配置
#支持httpd（即Apache集成方式）或svnserver
SVN_AUTH_MODE = 'httpd'
#Apache集成方式下的权限（authz）和htpasswd（用户&密码）文件位置
SVN_HTTPD_AUTHZ = 'd:\SVNMaster\Repos\\authz'
SVN_HTTPD_USERS = 'd:\SVNMaster\Repos\\htpasswd'
#HTTPD_HTPASSWD_FILE = 'd:\SVNMaster\Apache\bin\htpasswd.exe'
#SVN Server 服务方式时，用户/权限文件默认保存在每个库的conf文件夹下





#以下信息不要修改-------------以下信息不要修改-------------以下信息不要修改-------------以下信息不要修改-------------
#数据库配置
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '.\mos\dbs\sm_data.db')
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, '.\mos\dbs\db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

#以下信息不要修改
#表单加密
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
USERS_PER_PAGE = 10