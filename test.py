# -*- coding: utf8
import sys

import datetime
import logging

import math

from JiemoCodis import JimeoCodis

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/4/27 18:10
__author__ = 'haizhu'
from Jiemo_logger import Logger


# Logger();
# logger = logging.getLogger("markdown")
#
# logger.info("|name|value|")
# def pvCountFactor(currentPVCount, maxPVCount):
#     # print currentPVCount, maxPVCount
#     # y = (1 + sin(π * ((x - 2500) / 5000)))
#     # return 100 * ((1 + math.sin(math.pi * ((currentPVCount * 1.) / maxPVCount - 0.5))) / 2)
#     return 70 * ((1 + math.sin(math.pi * ((currentPVCount * 1.) / maxPVCount - 0.5))) / 2) + 30
#     pass
#
#
# for i in range(0, 101):
#     print pvCountFactor(i, 100)


print  "/root/shell/runEx.sh /data/java/jiemo-runner \"com.jiemo.runner.stats.PostScorePVAnalysisRunner {0}  ".format(
    2 * 24)
