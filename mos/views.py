#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__="EIXXIE"

from mos import app
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash,jsonify,json
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from functools import wraps
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from mos import app, db, lm
from mos.models.forms import UserForm,GroupForm,RepoForm,AuthItemForm
from mos.models.tables import User,Group,Repo,AuthItem,AuthPerm
from mos.utils.database import db_session,DBMaster,is_data_exist,GetData,SetData
from mos.utils.functions import get_now_time,Bool2Info,get_dir_time,getNum_inStr,Info2RW
from mos.utils.functions import create_repo,del_repo,change_repo,get_repo_path
from mos.utils.authz import gen_httpd_authzs,gen_httpd_users,refresh_all_users_auths,add_httpd_user,del_httpd_user,repwd_httpd_user
from config import SQLALCHEMY_DATABASE_URI,REPOS_DIRS,REPOS_BASE_URL,SVN_HTTPD_AUTHZ,SVN_AUTH_MODE

#定义管理员权限要求装饰函数
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return lm.unauthorized()
        if current_user.is_admin !=1:
            #return lm.unauthorized() 
            return redirect(url_for("mysvn"))
        return func(*args, **kwargs)
    return decorated_view

            
#从数据库中加载用户
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#获取当前用户信息
@app.before_request
def before_request():
    g.user = current_user

#404页面
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

#访问根目录时，判断是否已经登录
@app.route('/')
@app.route('/index')
@admin_required
def index():
    user = g.user
    #print(user)
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        return render_template('index.html',user=user)
    
#普通用户登录界面    
@app.route('/mysvn')
@login_required
def mysvn():
    user = g.user
    #print(user)
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        return render_template('mysvn.html',user=user)

#普通用户登录视图
@app.route('/users/mysvn')
@login_required
def user_mysvn():
    user = g.user
    user_auths =[]
    u = User.query.filter_by(username = user.username).first()
    user_auths=u.has_auths()
    #print(user_auths)
    groups = u.has_groups()
    for group in groups:
        ugroup = Group.query.filter_by(id = group[0]).first()
        group_auths = ugroup.has_auths()
        for group_auth in group_auths:
            user_auths.append(group_auth)
    return render_template('users/user_mysvn.html',user = u,user_auths=user_auths)   

#普通用户修改密码
@app.route('/users/mysvn/repwd', methods=['GET', 'POST'])
@login_required
def user_mysvn_repwd():
    info = ''
    user = g.user
    if request.method == 'POST':
        if len(request.form['password']) ==0: 
            info = '原密码不能为空！'
        elif request.form['password'] != user.password:
            info = '原密码不正确！'
        elif len(request.form['password_new1']) ==0 or len(request.form['password_new2']) ==0:
            info = '新密码不能为空'
        elif request.form['password_new1'] != request.form['password_new2']:
            info = '两次输入的新密码不一致'
        else:
            user = db.session.query(User).filter_by(username = user.username).first()
            user.password = request.form['password_new2']
            try:
                db.session.commit()
                info = '修改成功'
            except:
                info = '暂时无法修改，请稍后再试'
        return render_template('users/user_mysvn_repwd.html',user=user,info=info)
    else:
        user = User.query.filter_by(username = user.username).first()
        return render_template('users/user_mysvn_repwd.html',user=user)

#登录界面，判断填写信息与数据库信息是否一致
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if  current_user.is_authenticated:
        return redirect(url_for('index'))    
    elif request.method == 'POST':
        if len(request.form['password']) ==0 or len(request.form['username'])==0: 
            error = '用户名或密码不能为空！'
        else:
            u = User.query.filter_by(username = request.form['username']).first()
            if u==None or request.form['password'] != u.password: 
                error = '用户名或密码错误！'
            elif u.is_admin !=1:
                #error = '非管理员用户不能登录！'
                login_user(u)
                return redirect(url_for("mysvn"))
            elif u.is_active !=1:
                error = '用户未激活，请联系管理员！'
            else:
                login_user(u)
                return redirect(request.args.get("next") or url_for("index"))
    return render_template('login.html', error=error)

#注销用户
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#欢迎页面
@app.route('/welcome')
@admin_required
def welcome():
    infos={'url':REPOS_BASE_URL,'uri':REPOS_DIRS,'authmode':SVN_AUTH_MODE}
    user_all_nums = db_session.query(User).count()
    user_active_nums = db_session.query(User).filter(User.is_active=='1').count()
    group_all_nums = db_session.query(Group).count()
    group_active_nums = db_session.query(Group).filter(Group.status=='1').count() 
    repo_all_nums = db_session.query(Repo).count()
    repo_active_nums = db_session.query(Repo).filter(Repo.is_active=='1').count()    
    authitem_all_nums = db_session.query(AuthItem).count()
    datas={'user_all_nums':user_all_nums, 'user_active_nums':user_active_nums,\
           'group_all_nums':group_all_nums,'group_active_nums':group_active_nums,\
           'repo_all_nums':repo_all_nums,'repo_active_nums':repo_active_nums,\
           'authitem_all_nums':authitem_all_nums} 
    return render_template('welcome.html',paras=infos,datas=datas)

#----------------------------------以下为 用户管理 功能-----------------------------------------#
#用户管理页面
@app.route('/users', methods = ['GET', 'POST'])
@app.route('/users/<int:page>', methods = ['GET', 'POST'])
#@login_required
@admin_required
def user_list():
    searchitem =''
    if request.method == 'POST':
        if len(request.form['searchitem']) !=0: 
            # users = User.query.filter(or_(User.username.like('%'+request.form['searchitem']+'%',User.fullname.like('%'+request.form['searchitem']+'%')))).all()
            users = User.query.filter(User.username.like('%'+request.form['searchitem']+'%')).all()
            return render_template('users/user_list.html', users=users,searchitem = request.form['searchitem'])
    users = User.query.all()
    return render_template('users/user_list.html', users=users,searchitem = searchitem)

@app.route('/users/data', methods = ['GET', 'POST'])
@admin_required
def users_data():
    return GetData('users-json','all')

@app.route('/groups/data', methods = ['GET', 'POST'])
@admin_required
def groups_data():
    return GetData('groups-json','all')

@app.route('/repos/data', methods = ['GET', 'POST'])
@admin_required
def repos_data():
    return GetData('repos-json','all')

#增加用户
@app.route('/users/add', methods=['GET', 'POST'])
@admin_required
def user_add():
    info = ''
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        user.fullname = form.fullname.data
        user.username = form.username.data
        user.password = form.password.data
        user.email = form.email.data
        user.comments = form.comments.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        user.lasttime = get_now_time()
        try:
            DBMaster.save(user)
        except:
            info = '无法添加用户，请确认用户是否已存在'
            return render_template('users/user_add.html', form=form,info=info)
        return redirect('/users/info/' + user.username)
    else:
        info = '请按格式要求填写信息'
        return render_template('users/user_add.html', form=form,info=info)
    return render_template('users/user_add.html', form=form)

#删除用户
@app.route('/users/del/<username>', methods=['GET', 'POST'])
@admin_required
def user_del(username):
    info = ''
    user = User.query.filter_by(username = username).first()
    if request.method == 'POST':
        try:
            DBMaster.delete(user)
        except:
            info = '暂时无法删除用户，请稍后重试！'
            return render_template('users/user_del.html', info=info,user=user)
        info = '删除成功'
        return render_template('users/user_del.html',info=info)
    else:
        return render_template('users/user_del.html', user=user)
    
#修改用户信息
@app.route('/users/modify/<username>', methods=['GET', 'POST'])
@admin_required
def user_modify(username):
    info = ''
    form = UserForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username = username).first()
        user.fullname = form.fullname.data
        #user.username = form.username.data
        user.password = form.password.data
        user.email = form.email.data
        user.comments = form.comments.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        user.lasttime = get_now_time()
        try:
            db.session.commit()
        except:
            info = '暂时无法修改，请稍后再试'
            return render_template('users/user_modify.html',form=form,info=info)
        return redirect('/users/info/' + user.username)
    else:
        user = User.query.filter_by(username = username).first()
        form.fullname.data = user.fullname
        form.username.data = user.username
        form.password.data = '******'
        form.email.data = user.email
        form.comments.data = user.comments
        form.is_admin.data = user.is_admin
        form.is_active.data = user.is_active
        return render_template('users/user_modify.html',form=form)
    
#查询用户信息
@app.route('/users/info/<username>')
@admin_required
def user_info(username):
    u = User.query.filter_by(username = username).first()
    if u == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index')) 
    u.is_admin = Bool2Info('is_admin',u.is_admin)
    u.is_active = Bool2Info('is_active',u.is_active)
    groups = u.has_groups()
    return render_template('users/user_info.html',user = u,groups=groups)

#用户信息视图中，将用户从组中删除
@app.route('/users/leave/<groupid>+<userid>')
@admin_required
def user_leave_group(groupid,userid):
    u = User.query.filter_by(id = userid).first()
    u.leavegroup(groupid)
    return redirect('/users/info/' + u.username)

#用户信息视图中，将用户加入组
@app.route('/users/join/<userid>', methods=['GET', 'POST'])
@admin_required
def user_join_group(userid):
    if request.method == 'POST':
        u = User.query.filter_by(id = userid).first()
        print(request.form)
        groupids = request.form
        for groupid in groupids:
            print(getNum_inStr(groupid)[0])
            u.joingroup(getNum_inStr(groupid)[0])
        return redirect('/users/info/' + u.username)
    else:
        aviable_groups = Group.query.with_entities(Group.id, Group.groupname)
        return render_template('groups/group_select_for_user.html',userid = userid,groups=aviable_groups)
 
#查询用户权限
@app.route('/users/auth/<username>')
@admin_required
def user_auth(username):
    user_auths =[]
    u = User.query.filter_by(username = username).first()
    user_auths=u.has_auths()
    #print(user_auths)
    groups = u.has_groups()
    for group in groups:
        ugroup = Group.query.filter_by(id = group[0]).first()
        group_auths = ugroup.has_auths()
        for group_auth in group_auths:
            user_auths.append(group_auth)
    return render_template('users/user_auth.html',user = u,user_auths=user_auths)    



#----------------------------------以上为 用户管理 功能-----------------------------------------#


#----------------------------------以下为 用户组管理 功能-----------------------------------------#
#用户组管理页面
@app.route('/groups', methods = ['GET', 'POST'])
@app.route('/groups/list', methods = ['GET', 'POST'])
@app.route('/groups/list/<int:page>', methods = ['GET', 'POST'])
@admin_required
def group_list():
    if request.method == 'POST':
        if len(request.form['searchitem']) !=0: 
            groups = Group.query.filter(Group.groupname.like('%'+request.form['searchitem']+'%')).all()
            return render_template('groups/group_list.html', groups=groups)
    groups = Group.query.all()
    return render_template('groups/group_list.html', groups=groups)

#增加用户组
@app.route('/groups/add', methods=['GET', 'POST'])
@admin_required
def group_add():
    info = ''
    form = GroupForm()
    if form.validate_on_submit():
        group = Group()
        group.groupname = form.groupname.data
        group.comments = form.comments.data
        group.status = form.status.data
        group.lasttime = get_now_time()
        try:
            DBMaster.save(group)
        except:
            info = '无法添加用户组，请确认用户组是否已存在'
            return render_template('groups/group_add.html', form=form,info=info)
        return redirect('/groups/info/' + group.groupname)
    else:
        return render_template('groups/group_add.html', form=form)

#删除用户组
@app.route('/groups/del/<groupname>', methods=['GET', 'POST'])
@admin_required
def group_del(groupname):
    info = ''
    group = Group.query.filter_by(groupname = groupname).first()
    if request.method == 'POST':
        try:
            DBMaster.delete(group)
        except:
            info = '暂时无法删除用户，请稍后重试！'
            return render_template('groups/group_del.html', info=info,group=group)
        info = '删除成功'
        return render_template('groups/group_del.html',info=info)
    else:
        return render_template('groups/group_del.html', group=group)

#修改用户组信息
@app.route('/groups/modify/<groupname>', methods=['GET', 'POST'])
@admin_required
def group_modify(groupname):
    info = ''
    form = GroupForm()
    if form.validate_on_submit():
        group = db.session.query(Group).filter_by(groupname = groupname).first()
        group.groupname = form.groupname.data
        group.comments = form.comments.data
        group.status = form.status.data
        group.lasttime = get_now_time()
        try:
            db.session.commit()
        except:
            info = '暂时无法修改，请稍后再试'
            return render_template('groups/group_modify.html',form=form,info=info)
        return redirect('/groups/info/' + group.groupname)
    else:
        user = Group.query.filter_by(groupname = groupname).first()
        form.groupname.data = user.groupname
        form.comments.data = user.comments
        form.status.data = user.status
        return render_template('groups/group_modify.html',form=form)
    
#获取用户组信息
@app.route('/groups/info/<groupname>')
@admin_required
def group_info(groupname):
    group = Group.query.filter_by(groupname = groupname).first()
    if group == None:
        flash('Group ' + groupname + ' not found.')
        return redirect(url_for('index')) 
    group.status = Bool2Info('status',group.status)
    users = group.has_users()
    return render_template('groups/group_info.html',group = group,users=users)

#组信息视图中，将用户从组中删除
@app.route('/groups/remove/<groupid>+<userid>')
@admin_required
def group_remove_user(groupid,userid):
    u = User.query.filter_by(id = userid).first()
    u.leavegroup(groupid)
    group = Group.query.filter_by(id = groupid).first()
    return redirect('/groups/info/' + group.groupname)

#组信息视图中，将用户加入组
@app.route('/groups/join/<groupid>', methods=['GET', 'POST'])
@admin_required
def group_join_user(groupid):
    if request.method == 'POST':
        group = Group.query.filter_by(id = groupid).first()
        #print(request.form)
        userids = request.form
        for userid in userids:
            #print(getNum_inStr(userid)[0])
            #user = User.query.filter_by(id = getNum_inStr(userid)[0]).first()
            #user.joingroup(groupid)
            group.joinuser(getNum_inStr(userid)[0])
        return redirect('/groups/info/' + group.groupname)
    else:
        aviable_users = User.query.with_entities(User.id, User.fullname,User.username)
        return render_template('users/user_select_for_group.html',groupid = groupid,users=aviable_users)
    
#查询用户组权限
@app.route('/groups/auth/<groupname>')
@admin_required
def group_auth(groupname):
    group_auths =[]
    ugroup = Group.query.filter_by(groupname = groupname).first()
    group_auths = ugroup.has_auths()
    return render_template('groups/group_auth.html',group=ugroup,group_auths=group_auths)
#----------------------------------以上为 用户组管理 功能-----------------------------------------#

#----------------------------------以下为 SVN库管理 功能-----------------------------------------#
#SVN权限管理页面
@app.route('/repos', methods = ['GET', 'POST'])
@app.route('/repos/<int:page>', methods = ['GET', 'POST'])
@admin_required
def repo_list():
    repo_info=[]
    repo_list=[]
    repo_is_dir = 0
    searchitem = ''
    #判断有无搜索条件，如有则根据条件搜索，否则返回所有
    if request.method == 'POST':
        if len(request.form['searchitem']) !=0: 
            repos = Repo.query.filter(Repo.reponame.like('%'+request.form['searchitem']+'%')).all()
            searchitem = request.form['searchitem']
        else:
            repos = Repo.query.all()
    else:
        repos = Repo.query.all()
    #对配置库信息进行加工，检查物理存在与否、创建时间、修改时间等
    for repo in repos:
        repo_path = get_repo_path(repo.reponame)
        print(repo_path)
        try:
            repo_is_dir = os.path.isdir(repo_path)
        except:
            repo_info=[repo.reponame,'硬盘上不存在该配置库，请检查！','','','']
        if not repo_is_dir:
            repo_info=[repo.reponame, repo_path ,'',repo.comments,get_dir_time('ctime',repo_path),get_dir_time('mtime',repo_path),repo.is_active]
        else:
            repo_info=[repo.reponame,'硬盘上不存在该配置库，请检查！','','','','','']
        repo_list.append(repo_info)
    return render_template('repos/repo_list.html', repos=repo_list,searchitem=searchitem)



#增加SVN库
@app.route('/repos/add', methods=['GET', 'POST'])
@admin_required
def repo_add():
    info = ''
    form = RepoForm()
    if form.validate_on_submit():
        repo = Repo()
        repo.reponame = form.reponame.data
        repo.comments = form.comments.data
        repo.is_active = form.is_active.data
        repo.lasttime = get_now_time()
        if create_repo(form.reponame.data):
            try:
                DBMaster.save(repo)
            except:
                info = '无法创建配置库，请检查是否已存在同名配置库！'
                return render_template('repos/repo_add.html', form=form,info=info)
        else:
            info = '无法创建配置库，请检查操作系统权限！'
            return render_template('repos/repo_add.html', form=form,info=info)
        return redirect('/repos/info/' + repo.reponame)
    else:
        return render_template('repos/repo_add.html', form=form)


#删除SVN库
@app.route('/repos/del/<reponame>', methods=['GET', 'POST'])
@admin_required
def repo_del(reponame):
    info = ''
    repo = Repo.query.filter_by(reponame = reponame).first()
    repo.is_active = Bool2Info('is_active',repo.is_active)
    if request.method == 'POST':
        if del_repo(reponame):
            try:
                DBMaster.delete(repo)
            except:
                info = '数据库异常，请稍后重试！'
                return render_template('repos/repo_del.html', info=info,repo=repo)
            info = '删除成功'
            return render_template('repos/repo_del.html',info=info)
        else:
            info = '暂时无法删除配置库文件夹，请稍后重试或手动删除！'
            return render_template('repos/repo_del.html', info=info,repo=repo)            
    else:
        return render_template('repos/repo_del.html', repo=repo)
    
#修改SVN库信息
@app.route('/repos/modify/<reponame>', methods=['GET', 'POST'])
@admin_required
def repo_modify(reponame):
    info = ''
    form = RepoForm()
    if form.validate_on_submit():
        repo = db.session.query(Repo).filter_by(reponame = reponame).first()
        repo.reponame = form.reponame.data
        repo.comments = form.comments.data
        repo.is_active = form.is_active.data
        repo.lasttime = get_now_time()
        if change_repo(reponame,form.reponame.data):
            try:
                db.session.commit()
            except:
                info = '暂时无法修改，请稍后再试'
                return render_template('repos/repo_modify.html',form=form,info=info)
        else:
            info = '暂时无法修改，请稍后再试'
            return render_template('repos/repo_modify.html',form=form,info=info)            
        return redirect('/repos/info/' + repo.reponame)
    else:
        repo = Repo.query.filter_by(reponame = reponame).first()
        form.reponame.data = repo.reponame
        form.comments.data = repo.comments
        form.is_active.data = repo.is_active
        return render_template('repos/repo_modify.html',form=form)
    
#查询SVN库信息
@app.route('/repos/info/<reponame>')
@admin_required
def repo_info(reponame):
    authitems=[]
    repo = Repo.query.filter_by(reponame = reponame).first()
    if repo == None:
        flash('Repo ' + reponame + ' not found.')
        return redirect(url_for('index')) 
    repo.is_active = Bool2Info('is_active',repo.is_active) 
    authitems = repo.has_Authitems()
    return render_template('repos/repo_info.html',repo = repo,authitems=authitems)
#----------------------------------以上为 SVN库管理 功能-----------------------------------------#

#----------------------------------以下为 SVN库权限配置项管理 功能-----------------------------------------#
#SVN配置项管理页面
@app.route('/auth/item', methods = ['GET', 'POST'])
@app.route('/auth/item/<int:page>', methods = ['GET', 'POST'])
@admin_required
def auth_item_list():
    auth_items=[]
    searchitem = ''
    #判断有无搜索条件，如有则根据条件搜索，否则返回所有
    if request.method == 'POST':
        print(searchitem)
        if len(request.form['searchitem']) !=0: 
            #auth_items = AuthItem.query.filter(AuthItem.repo_id.like('%'+request.form['searchitem']+'%')).all()
            auth_items = GetData('authitems',request.form['searchitem'])
            searchitem = request.form['searchitem']
        else:
            auth_items = GetData('authitems','all')
    else:
        auth_items = GetData('authitems','all')
    return render_template('auths/auth_item_list.html', auth_items=auth_items,searchitem=searchitem)



#增加配置项
@app.route('/auth/item/add', methods=['GET', 'POST'])
@admin_required
def auth_item_add():
    info = ''
    form = AuthItemForm()
    #提交添加信息时，判断是否已经存在相同项
    if form.validate_on_submit():
        auth_item = AuthItem()
        repo_name = form.repo_name.data.reponame
        auth_item.repo_id = form.repo_name.data.id
        auth_item.authitem = form.authitem.data
        #print(repo_name + '   ' + str(auth_item.repo_id))
        if is_data_exist('authitem',[str(auth_item.repo_id),auth_item.authitem]):
            info = '配置项已存在，请不要重复添加'
            return render_template('auths/auth_item_add.html', form=form,info=info)            
        try:
            DBMaster.save(auth_item)
            #SetData('authitem',[auth_item.repo_name,auth_item.authitem])
        except:
            info = '无法创建配置项，请检查系统配置！'
            return render_template('auths/auth_item_add.html', form=form,info=info)
        #如成功，则返回刚刚添加的信息页面
        return redirect('/auth/item/info/' + str(GetData('authitemid',[repo_name,auth_item.authitem])))
    #首次进入添加页面时
    else:
        return render_template('auths/auth_item_add.html', form=form)


#删除配置项
@app.route('/auth/item/del/<authitemid>', methods=['GET', 'POST'])
@admin_required
def auth_item_del(authitemid):
    info = ''
    authitem = AuthItem.query.filter_by(id = authitemid).first()
    authitems = GetData('authiteminfo',[str(authitem.id)])
    if request.method == 'POST':
        try:
            DBMaster.delete(authitem)
        except:
            info = '数据库异常，请稍后重试！'
            return render_template('auths/auth_item_del.html', info=info,authitems=authitems)
        info = '删除成功'
        return render_template('auths/auth_item_del.html',info=info)
    else:
        return render_template('auths/auth_item_del.html', authitems=authitems)
    
#修改配置项信息
@app.route('/auth/item/modify/<authitemid>', methods=['GET', 'POST'])
@admin_required
def auth_item_modify(authitemid):
    info = ''
    form = AuthItemForm()
    if form.validate_on_submit():
        authitem = db.session.query(AuthItem).filter_by(id = authitemid).first()
        authitem.repo_id = form.repo_name.data.id
        authitem.authitem = form.authitem.data
        if is_data_exist('authitem',[str(authitem.repo_id),authitem.authitem]):
            info = '配置项已存在，请不要重复'
            return render_template('auths/auth_item_modify.html', form=form,info=info)           
        try:
            db.session.commit()
        except:
            info = '暂时无法修改，请稍后再试'
            return render_template('auths/auth_item_modify.html',form=form,info=info)
        return redirect('/auth/item/info/' + authitemid)
    else:
        authitem = AuthItem.query.filter_by(id = authitemid).first()
        #form = AuthItemForm(repo_name=[db.session.query(Repo).filter_by(id = authitem.repo_id).first()])
        #form.repo_name.data = db.session.query(Repo).filter_by(id = authitem.repo_id).first()
        form.authitem.data = authitem.authitem
        return render_template('auths/auth_item_modify.html',form=form)
    
#查询配置项信息
@app.route('/auth/item/info/<authitemid>')
@admin_required
def auth_item_info(authitemid):
    authitem = AuthItem.query.filter_by(id = authitemid).first()
    authitems = GetData('authiteminfo',[str(authitem.id)])
    if authitem == None:
        flash('Authitem ' + authitemid + ' not found.')
        return redirect(url_for('index'))   
    return render_template('auths/auth_item_info.html',authitems = authitems)
#----------------------------------以上为 SVN库权限配置项管理 功能-----------------------------------------#

#----------------------------------以下为 SVN权限管理 功能-----------------------------------------#
#SVN权限管理页面
@app.route('/auth/perm/<itemid>', methods = ['GET', 'POST'])
@admin_required
def auth_item_perm(itemid):
    print(itemid)
    authitem = AuthItem.query.filter_by(id = itemid).first()
    authusers = authitem.has_authusers()
    authgroups = authitem.has_authgroups()
    authitems = GetData('authiteminfo',[str(itemid)])
    return render_template('auths/auth_perm_info.html',authitemid=itemid,authitems = authitems,authusers=authusers,authgroups=authgroups)

#配置项信息视图中，将用户权限从配置项中删除
@app.route('/auth/user/remove/<itemid>+<userid>')
@admin_required
def auth_remove_user(itemid,userid):
    authitem = AuthItem.query.filter_by(id = itemid).first()
    authitem.removeuser(userid)
    return redirect('/auth/perm/' + itemid)

#配置项信息视图中，将用户组权限从配置项中删除
@app.route('/auth/group/remove/<itemid>+<groupid>')
@admin_required
def auth_remove_group(itemid,groupid):
    authitem = AuthItem.query.filter_by(id = itemid).first()
    authitem.removegroup(groupid)
    return redirect('/auth/perm/' + itemid)

#配置项信息视图中，加入用户权限
@app.route('/auth/user/join/<itemid>', methods=['GET', 'POST'])
@admin_required
def auth_join_user(itemid):
    userlist=[]
    if request.method == 'POST':
        authitem = AuthItem.query.filter_by(id = itemid).first()
        print(request.form.getlist('userlist[]'))
        authperm = request.form['authperm']
        authtype= Info2RW(authperm) 
        userlist = request.form.getlist('userlist[]')
        for user in userlist:
            print(user)
            authitem.joinuser(user,authtype)
        return redirect('/auth/perm/' + itemid)
    else:
        return render_template('auths/auth_perm_add_user.html',itemid = itemid,userlist=userlist)

#配置项信息视图中，加入用户组权限
@app.route('/auth/group/join/<itemid>', methods=['GET', 'POST'])
@admin_required
def auth_join_group(itemid):
    grouplist=[]
    if request.method == 'POST':
        authitem = AuthItem.query.filter_by(id = itemid).first()
        print(request.form.getlist('grouplist[]'))
        authperm = request.form['authperm']
        authtype= Info2RW(authperm) 
        grouplist = request.form.getlist('grouplist[]')
        for group in grouplist:
            print(group)
            authitem.joingroup(group,authtype)
        return redirect('/auth/perm/' + itemid)
    else:
        return render_template('auths/auth_perm_add_group.html',itemid = itemid,grouplist=grouplist) 

#重新生成Authz文件    
@app.route('/auth/perm/refresh', methods = ['GET', 'POST'])
@admin_required
def auth_perm_refresh():
    #调用Authz文件生成函数
    refresh_all_users_auths()
    return render_template('auths/auth_perm_refresh.html')
#----------------------------------以上为 SVN权限管理 功能-----------------------------------------#

#----------------------------------以下为 其它 功能-----------------------------------------#
#Howto页面
@app.route('/howto', methods = ['GET', 'POST'])
def howto():
    return render_template('howto.html')

#SVN_Auth_Howto页面
@app.route('/auth_howto', methods = ['GET', 'POST'])
def auth_howto():
    return render_template('auth_howto.html')