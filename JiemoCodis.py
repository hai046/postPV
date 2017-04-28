# -*- coding: utf8
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
# 2017/3/27 11:20
__author__ = 'haizhu'

import BfdCodis as codis

import JiemoConfig


class JimeoCodis:
    def getCodis(self, debug=False):
        c = JiemoConfig.Config()
        proxyPath = "/zk/codis/db_jiemo/proxy"
        if not c.isProductionEnvironment():
            proxyPath = "/zk/codis/db_jiemoapp-test/proxy"

        if debug:
            print "isProductionEnvironment=", c.isProductionEnvironment(), "  proxyPath =", proxyPath
        client = codis.BfdCodis("zk.d.jiemoapp.com:2181", proxyPath)

        return client
