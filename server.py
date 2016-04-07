#!/usr/bin/env python
# -*- coding: utf-8 -*- 
__author__="EIXXIE"

import sys,os
from mos import app
from config import SERVER_PORT

#将mos文件夹添加到系统变量中，以便import
sys.path.append(os.path.dirname(app.root_path))
#启动MOS
app.run(host='0.0.0.0',port=SERVER_PORT,debug=True)

#print(sys.path)
