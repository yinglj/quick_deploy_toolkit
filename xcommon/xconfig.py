# -*- coding:utf-8 -*-
from configparser import RawConfigParser, NoOptionError
import re
import sys

# 界面显示配置定义，这块可以根据需要调整
COLUMN_NUM = 3
HOST_WIDTH = 12
USER_WIDTH = 12
IP_WIDTH = 16
COLUMN_WIDTH = HOST_WIDTH + USER_WIDTH + IP_WIDTH
BLOCK_NUM = 10
OUT_PUT_WIDTH = COLUMN_NUM * COLUMN_WIDTH + COLUMN_NUM + 1
STR_OUTPUT_PROMOTE = "# host:"
# 常量定义
ENCRYPT_PASSWORD_MODE = 0
DECRYPT_PASSWORD_MODE = 1

INPUT_ = input
if 2 == sys.version_info.major:
    INPUT_ = raw_input


LANGUAGE_MAP = {
    '0': {
        "login_hint": " 帮  助 $  输入HOST.NO,登录对应主机",
        "welcome_hint": "欢迎使用远程登录系统",
        "hostno_hint": "HOST.NO",
        "user_hint": "用户",
        "iplist_hint": "IP列表",
        "domain_hint": " exit: 退出 | set domain: 切换主机域",
        "cur_domain_hint": " 当前域：",
    },  
    '1': {
        "login_hint": " HELP $  raw_input HOST.NO TO LOGIN",
        "welcome_hint": "welcome to use scripts for remoting login",
        "hostno_hint": "HOST.NO",
        "user_hint": "login",
        "iplist_hint": "IP LIST",
        "domain_hint": " exit: quit | set domain: SWITCH DOMAIN",
        "cur_domain_hint": " Current domain:",
    },  
}


class XConfigParser(RawConfigParser):
    def get(self, section, option):
        try:
            return RawConfigParser.get(self, section, option)
        except NoOptionError:
            return None


class XLangHelper(object):
    @staticmethod
    def get_hint(lang, hint_id):
        return LANGUAGE_MAP[lang][hint_id]
