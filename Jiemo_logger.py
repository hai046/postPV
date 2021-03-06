# -*- coding: utf8
import os
import sys

import logging

import datetime

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/3/27 15:50
__author__ = 'haizhu'


class Logger:
    def __init__(self, log_dir="/data/log/jiemo-postPV"):
        self._logDir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        logging.basicConfig(
            filename=os.path.join(log_dir, "main.log_{0}".format((datetime.datetime.now()).strftime("%Y-%m-%d"))),
            level=logging.INFO,
            format='[%(asctime)s %(levelname)s %(process)d %(filename)s %(lineno)d] - %(message)s')

        # 初始化暑促
        logger = logging.getLogger("markdown")
        logger.setLevel(logging.INFO)

        file = os.path.join(self._logDir, "score.md");

        if os.path.exists(file):
            os.remove(file)

        fh = logging.FileHandler(file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        pass
