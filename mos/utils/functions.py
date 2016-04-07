#!/usr/bin/env python
# -*- coding: utf-8 -*- 
__author__="EIXXIE"

from wtforms import Form, BooleanField, TextField, PasswordField, validators
import os,os.path,time, platform,re
from config import REPOS_DIRS
from config import REPOS_BASE_URL

#返回当前时间
def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
def get_now_time2():
    return time.strftime("%Y-%m-%d %H-%M-%S",time.localtime(time.time()))

#获得文件夹的创建时间和最后修改时间
def get_dir_time(timetype,repo_path):
    if timetype == 'ctime':
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.stat(repo_path).st_ctime))
    elif timetype == 'mtime':
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.stat(repo_path).st_mtime))
    else:
        return '参数错误'

#获取配置库基本信息
def repo_info(repo_path):
    #创建时间
    dir_ctime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.stat(repo_path).st_ctime))
    #最后修改时间
    dir_mtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.stat(repo_path).st_mtime))
    return [repo_path.split('\\')[-1],repo_path,dir_ctime,dir_mtime]

#从硬盘获取SVN库列表
def get_repo_list():
    repo_list=[]
    try:
        dir_list = os.listdir(REPOS_DIRS)
    except:
        #文件夹不存在
        return []
    #print(dir_list)
    for dir in dir_list:
        dir_path = REPOS_DIRS + dir
        if os.path.isdir(dir_path):
            dir_stat = os.stat(dir_path)
            repo_list.append(repo_info(dir_path))
    #print(repo_list)
    return repo_list

#从获得SVN库物理地址
def get_repo_path(reponame):
    return REPOS_DIRS + reponame

#从获得SVN库网络地址
def get_repo_url(reponame):
    return REPOS_BASE_URL + reponame
    
    
#创建配置库
def create_repo(reponame):
    sysstr = platform.system()
    if(sysstr =="Windows"):
        #os.system("mkdir " + REPOS_DIRS + reponame)
        subprocess.check_output(['svnadmin', 'create',os.path.join(REPOS_DIRS,reponame)]).decode('utf-8').strip()
    elif(sysstr == "Linux"):
        #os.system("mkdir -p " + REPOS_DIRS + reponame)
        subprocess.check_output(['svnadmin', 'create',os.path.join(REPOS_DIRS,reponame)]).decode('utf-8').strip()
    else:
        pass
    if os.path.isdir(REPOS_DIRS + reponame):
        return True
    return False

#删除配置库
def del_repo(reponame):
    sysstr = platform.system()
    if(sysstr =="Windows"):
        os.system("rd /s /q  " + REPOS_DIRS + reponame)
    elif(sysstr == "Linux"):
        os.system("rm -rf " + REPOS_DIRS + reponame)
    else:
        pass
    if os.path.isdir(REPOS_DIRS + reponame):
        return False
    return True

#修改配置库名称
def change_repo(before_name,after_name):
    sysstr = platform.system()
    if(sysstr =="Windows"):
        #print("move  " + REPOS_DIRS + before_name + ' ' + REPOS_DIRS + after_name)
        os.system("move  " + REPOS_DIRS + before_name + ' ' + REPOS_DIRS + after_name)
    elif(sysstr == "Linux"):
        os.system("mv  " + REPOS_DIRS + before_name + ' ' + REPOS_DIRS + after_name)
    else:
        pass
    if os.path.isdir(REPOS_DIRS + after_name):
        return True
    return False

#将布尔值转换为特定文字
def Bool2Info(name,value):
    if (name=="is_admin"):
        if (value==1):return "管理员"
        else:return "普通用户"
    if (name=="is_active"):
        if (value==1):return "可用"
        else:return "已禁用"
    if (name=="status"):
        if (value==1):return "可用"
        else:return "已禁用"
    else:return "参数错误"

def Info2RW(value):
    if (value=='write'):
        return '读写'
    elif(value=='readonly'):
        return '只读'
    elif(value=='none'):
        return '禁止'
    elif(value==''):
            return '禁止'    
    elif(value=='r'):
            return '只读'    
    elif(value=='rw'):
            return '读写'   
    elif(value=='禁止'):
            return ' '    
    elif(value=='只读'):
            return 'r'    
    elif(value=='读写'):
            return 'rw'     
    else:
        return "参数错误"

#获得list数组的index
def getNum_inStr(str):
    num = re.findall(r'(\w*[0-9]+)\w*',str)
    return num


        