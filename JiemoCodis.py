# -*- coding: utf8
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/3/27 11:20
__author__ = 'haizhu'

import BfdCodis as codis

import JiemoConfig


class JimeoCodis:
    def getCodis(self):
        c = JiemoConfig.Config()
        proxyPath = "/zk/codis/db_jiemo/proxy"
        if not c.isProductionEnvironment:
            proxyPath = "/zk/codis/db_jiemoapp-test/proxy"

        client = codis.BfdCodis("zk.d.jiemoapp.com:2181", proxyPath)

        return client