# -*- coding: utf8
import os
import sys

import logging

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/3/27 15:50
__author__ = 'haizhu'


class Logger:
    def __init__(self, logDir="/data/log/postPV"):
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        logging.basicConfig(filename=os.path.join(logDir, "main.log"), level=logging.DEBUG,
                            format='[%(asctime)s %(levelname)s %(process)d %(filename)s %(lineno)d] - %(message)s')
