# -*- coding: utf8
import sys

import datetime
import logging

from JiemoCodis import JimeoCodis

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/4/27 18:10
__author__ = 'haizhu'
from Jiemo_logger import Logger

Logger();
logger = logging.getLogger("markdown")

logger.info("|name|value|")
