#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------------------
# Copyright (c) 2016 project AutomicDeploy
# This script is licensed under GNU GPL version 2.0 or above
# author: yinglj@gmail.com
# ---------------------------------------------------------------------------------------
# Expect script to supply root/admin password for remote ssh server and execute command.
# user = User Name of remote Linux/UNIX server, no hostname
# password = Password of remote Linux/UNIX server, for root user.
# host = IP Addreess of remote Linux/UNIX server, no hostname
# ---------------------------------------------------------------------------------------

import os
import sys
import pexpect
import time
import re
import collections
import threading
import base64
import argparse
from typing import OrderedDict
from collections import Counter
from collections import defaultdict
from collections import OrderedDict
from xcommon.config import *


class CRemoteCmd3(object):
    def __init__(self):
        self.mutex = threading.Lock()
        self.cfg = XConfigParser(allow_no_value=True)
        self.spec_cmd = ""
        self.cmds = []
        self.mapStdout = defaultdict(list)
        self.background = ""
        self.hostcfg = '''please config filename: host.cfg
    ================================================================================
    content example:
    [host1]
    domain = database
    user = mongodb
    password = oXV4LYH2EUQiHpcg
    host = 10.10.13.170
    workdir = /home/mongodb
    ================================================================================
    '''

    def read_cfg(self, filename):
        self.cfg.read(filename)
        '''
        s = cfg.sections()
        print 'section:', s
        for i in s:
            print cfg.options(i)
            for j in cfg.options(i):
                print j,cfg.get(i, j)
            print cfg.items(i)
        '''

    # diff host1 or ip_addr

    def init_command(self, domain_config, spec_host, command):
        self.read_cfg(sys.path[0]+"/host.cfg")
        # read_cfg(domain_config)
        s = self.cfg.sections()
        cmd_argv = []
        '''
        spec_host = ""
        if sys.argv[1] in s:    #host1 in command
            cmd_argv = sys.argv[2:]
            spec_host = sys.argv[1]
        for i in s:
            host = ""
            for j in cfg.options(i):
                if j == 'host':
                    host=cfg.get(i,j)
                    if host == sys.argv[1]:    #ip in host.cfg
                        spec_host = i
                        cmd_argv = sys.argv[2:]
                    break
        if spec_host == "":
            cmd_argv = sys.argv[1:]
        for i in cmd_argv:
            command += i+" "
        #print "command:"+command
        #print "spec_host:"+spec_host
        '''
        user = ""
        password = ""
        host = ""
        workdir = ""
        domain = ""
        hostno = ""
        thread_list = []
        for i in s:
            user = ""
            password = ""
            host = ""
            workdir = ""
            port = "22"
            for j in self.cfg.options(i):
                if j == 'user':
                    user = self.cfg.get(i, j)
                if j == 'password':
                    password = self.cfg.get(i, j)
                if j == 'host':
                    host = self.cfg.get(i, j)
                if j == 'port':
                    port = self.cfg.get(i, j)
                if j == 'workdir':
                    workdir = self.cfg.get(i, j)
                if j == 'domain':
                    domain = self.cfg.get(i, j)
            if domain_config != "" and domain_config != "all" and domain != domain_config:
                continue

            hostno = i
            if spec_host == i or spec_host == host or spec_host == "":
                my_thread = threading.Thread(target=self.onethread_run_ssh, args=(
                    domain, hostno, user, password, host, port, workdir, command,))
                #print "-------------------1----------------------------------------------------------------------"
                my_thread.start()
                #print "-------------------2----------------------------------------------------------------------"
                thread_list.append(my_thread)
        for thread in thread_list:
            thread.join()
        # 按key列进行排序
        for key, value in sorted(self.mapStdout.items(), key=lambda dict: dict[0], reverse=False):
            for i in value:
                print(i, end='')
        # mapStdout.clear()

    def onethread_run_ssh(self, domain, hostno, user, password, host, port, workdir, command):
        spec_cmd = "ssh -p {} -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no {} {}@{} ".format(
            port, background, user, host)
        spec_cmd += command
        # print("spec_cmd:"+spec_cmd)
        self.run_ssh(domain, hostno, host, spec_cmd, password)

    def run_command(self, domain_config, spec_host, command):
        self.init_command(domain_config, spec_host, command)

    def run_ssh(self, domain, hostno, host, cmd, passwd):
        child = pexpect.spawn(cmd)
        try:
            child.expect('(!*)password:(!*)')
            passwd_decode = base64.b64decode(passwd)
            if passwd_decode[-1] == '\n':
                passwd_decode = passwd_decode[:-1]
            _ = child.sendline(passwd_decode)  # base64解码后多一个回车键符，需要剪掉一位
        except pexpect.EOF:
            self.output_info(domain, hostno, host,
                             "can not connect to {}-{}-{}\n".format(domain, hostno, host))
            if child.isalive():
                child.close(force=True)
            return
        except pexpect.TIMEOUT:
            self.output_info(domain, hostno, host,
                             "connect timeout {}-{}-{}\n".format(domain, hostno, host))
            if child.isalive():
                child.close(force=True)
            return

        child.expect(pexpect.EOF, timeout=60)
        if self.mutex.acquire():
            abc = child.before
            import chardet
            d = chardet.detect(abc)
            output_msg = child.before.decode('unicode_escape')
            self.output_info(domain, hostno, host, output_msg)
        self.mutex.release()
        child.close(force=True)

    def output_info(self, domain, hostno, host, msg):
        index_count = OUT_PUT_WIDTH - \
            len(domain) - len(hostno) - len(host) + 1
        self.mapStdout[host].append("-"*OUT_PUT_WIDTH + "\n")
        self.mapStdout[host].append(
            "{0}\033[36;1m{1} {2} {3: <{4}}\033[0m#\n".format(STR_OUTPUT_PROMOTE, domain, hostno, host, index_count))
        self.mapStdout[host].append("-"*OUT_PUT_WIDTH + "\n")
        self.mapStdout[host].append(msg)
        self.mapStdout[host].append("-"*OUT_PUT_WIDTH + "\n")

    def Usage(self, command):
        print("usage:"+command+" [host1] command")
        print(self.hostcfg)
        print("example: "+command+" 'ls -l'")
        print("example: "+command+" host1 'ls -l'")


if __name__ == '__main__':
    cCRemoteCmd3 = CRemoteCmd3()
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', default='all', help='--domain all')
    parser.add_argument('--ip', default='', help='--ip host_ip')
    args, unknowns = parser.parse_known_args()
    command = ' '.join(unknowns).replace("\"", "\\\"").replace(
        "$", "\\$")  # .replace("\'", "\\'")
    # print ("{} unknowns:{}".format(args, unknowns))
    time.sleep(0.1)

    if command == "":
        parser.print_usage()
    else:
        try:
            # command=""
            #print len(sys.argv)
            if command[-1] == "&":  # 命令行加了&，解析成后台命令
                background = "-f -n"
            else:
                background = ""

            cCRemoteCmd3.run_command(args.domain, args.ip, command)
            time.sleep(0)
        except KeyboardInterrupt as e:
            print(e)
        except IOError as e:
            print(e)
        except ValueError as e:
            print(e)
        finally:
            pass
