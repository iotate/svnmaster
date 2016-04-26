# -*- coding: utf-8 -*- 
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.login import LoginManager
#from flask.ext.openid import OpenID
from config import basedir
from config import REPOS_DIRS
from config import REPOS_BASE_URL

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

import mos.views

