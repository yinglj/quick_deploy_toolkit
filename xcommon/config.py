# -*- coding:utf-8 -*-
from configparser import RawConfigParser, NoOptionError

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


class XConfigParser(RawConfigParser):
    def get(self, section, option):
        try:
            return RawConfigParser.get(self, section, option)
        except NoOptionError:
            return None
