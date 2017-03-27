# -*- coding: utf8
import json
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/3/27 11:26
__author__ = 'haizhu'
from kazoo.client import KazooClient


class Config:
    def __init__(self):
        self._isProductionEnvironment = None

    def isProductionEnvironment(_self):
        if _self._isProductionEnvironment != None:
            return _self._isProductionEnvironment
        zk = KazooClient("zk.d.jiemoapp.com:2181")
        zk.start()
        isProductionEnvironment = json.loads(zk.get("/jiemo/config/ProductionEnviornment")[0]);
        if isProductionEnvironment:
            print "外网"
        zk.stop()
        _self._isProductionEnvironment = isProductionEnvironment
        return isProductionEnvironment


if __name__ == '__main__':
    cfg = Config()
