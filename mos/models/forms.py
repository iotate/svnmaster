#!/usr/bin/env python
# -*- coding: utf-8 -*- 
__author__="EIXXIE"

from flask.ext.wtf import Form,validators
from wtforms import StringField, BooleanField,TextAreaField,SelectField,SelectMultipleField,RadioField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from mos.models.tables import User,Group,Repo,getRepoFactory,getGroupFactory

#新增用户Form
class UserForm(Form):
    fullname = StringField('fullname', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    comments = StringField('comments')
    is_admin = BooleanField('is_admin')
    is_active = BooleanField('is_active')

#新增用户组Form    
class GroupForm(Form):
    groupname = StringField('groupname', validators=[DataRequired()])
    comments = StringField('comments', validators=[DataRequired()])
    status = BooleanField('status')

#新增配置库Form    
class RepoForm(Form):
    reponame = StringField('reponame', validators=[DataRequired()])
    comments = StringField('comments')
    is_active = BooleanField('is_active')

#新增配置项Form    
class AuthItemForm(Form):
    #repo_id = StringField('repo_id', validators=[DataRequired()])
    repo_name = QuerySelectField(u'Repo',
                            query_factory=getRepoFactory(['id', 'reponame']),
                            get_label='reponame') 
    authitem = StringField('authitem', validators=[DataRequired()])
    