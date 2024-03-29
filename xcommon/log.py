# coding:utf-8
import logging
import logging.handlers
import time
import datetime
from config import CConfigHandle
import os
import sys


class XLogger(object):
    def __init__(self, name, config_file='config.xml'):
        # log_path是存放日志的路径
        self.cur_path = os.path.dirname(os.path.realpath(__file__))
        self.log_path = os.path.join(os.path.dirname(self.cur_path), 'logs')

        # 如果不存在这个logs文件夹，就自动创建一个
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        cConfigHandle = CConfigHandle(config_file)
        logpath = cConfigHandle.get_value('config', 'logpath')
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)
        # 读取日志文件容量，转换为字节
        self.logsize = 1024*1024*int(cConfigHandle.get_value('config', 'logsize'))
        # 读取日志文件保存个数
        self.lognum = int(cConfigHandle.get_value('config', 'lognum'))
        # 日志文件名：由用例脚本的名称，结合日志保存路径，得到日志文件的绝对路径
        self.logname = sys.argv[0].split(
            '/')[-1].split('.')[0] + datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S_%f') + '.log'
        self.logname = os.path.join(logpath, self.logname)

        # 文件的命名
        #self.logname = os.path.join(log_path, '%s.log'%time.strftime('%Y_%m_%d'))
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        # 日志输出格式
        #self.formatter = logging.Formatter('[%(asctime)s]-%(name)s-%(levelname)s-%(message)s')
        self.formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - %(name)s[:%(lineno)d][%(levelname)s] %(message)s'
            # , datefmt='%Y-%m-%d,%H:%M:%S.%f'
        )

        # 创建一个FileHandler,存储日志文件
        fh = logging.handlers.RotatingFileHandler(
            self.logname, maxBytes=self.logsize, backupCount=self.lognum, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # 创建一个StreamHandler,用于输出到控制台
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(self.formatter)
        self.logger.addHandler(sh)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def Fatal(self, message):
        self.logger.critical(message)
