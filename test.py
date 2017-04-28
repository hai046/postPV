# -*- coding: utf8
import sys

import datetime

from JiemoCodis import JimeoCodis

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/4/27 18:10
__author__ = 'haizhu'

print str(datetime.datetime.now())

codis = JimeoCodis().getCodis(debug=True);
# 存储处理
key = "z.hplt"
codis.delete(key)
