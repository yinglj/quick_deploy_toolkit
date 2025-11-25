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
import time
import threading
import base64
import argparse
from collections import defaultdict
import pexpect
from xcommon.xconfig import *
from xcommon.util import XUtil


class CRemoteCmd3(object):
    '''
    CRemoteCmd3
    '''
    def __init__(self):
        self.mutex = threading.Lock()
        self.cfg = XConfigParser(allow_no_value=True)
        self.spec_cmd = ""
        self.cmds = []
        self.map_stdout = defaultdict(list)
        self.background = ""
        self.lang = ''
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
        '''
        read config
        '''
        self.cfg.read(filename)

    # diff host1 or ip_addr

    def init_command(self, domain_config, spec_host, command):
        '''
        initial command
        '''
        self.read_cfg(XUtil.get_host('host.cfg'))

        # read_cfg(domain_config)
        s = self.cfg.sections()
        # cmd_argv = []
        # spec_host = ""
        # if sys.argv[1] in s:    #host1 in command
        #     cmd_argv = sys.argv[2:]
        #     spec_host = sys.argv[1]
        # for i in s:
        #     host = ""
        #     for j in cfg.options(i):
        #         if j == 'host':
        #             host=cfg.get(i,j)
        #             if host == sys.argv[1]:    #ip in host.cfg
        #                 spec_host = i
        #                 cmd_argv = sys.argv[2:]
        #             break
        # if spec_host == "":
        #     cmd_argv = sys.argv[1:]
        # for i in cmd_argv:
        #     command += i+" "
        # #print "command:"+command
        # #print "spec_host:"+spec_host
        user = ""
        password = ""
        host = ""
        workdir = ""
        domain = ""
        hostno = ""
        background = ""
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
                if j == 'background':
                    domain = self.cfg.get(i, j)
            if domain_config != "" and domain_config != "all" and domain != domain_config:
                continue

            if i == "global":
                self.lang = self.cfg.get(i, "LANG")
                continue

            hostno = i
            if spec_host == i or spec_host == host or spec_host == "":
                my_thread = threading.Thread(target=self.onethread_run_ssh, args=(
                    domain, hostno, user, password, host, port, workdir, command, background))
                #print "-------------------1----------------------------------------------------------------------"
                my_thread.start()
                #print "-------------------2----------------------------------------------------------------------"
                thread_list.append(my_thread)
        for thread in thread_list:
            thread.join()
        # 按key列进行排序
        for _, value in sorted(self.map_stdout.items(), key=lambda dict: dict[0], reverse=False):
            for i in value:
                print(i, end='')
        print("-"*OUT_PUT_WIDTH + "\n")
        # map_stdout.clear()

    def onethread_run_ssh(self, domain, hostno, user, password, host, port, workdir, command, background):
        '''
        one thread run ssh
        '''
        if os.path.isfile(password):
            spec_cmd = f"ssh -p {port}  -o PubkeyAuthentication=yes -o StrictHostKeyChecking=no -t {background} -i {password} {user}@{host} "
            spec_cmd += command
            # print("spec_cmd:"+spec_cmd)
            self.run_ssh_pem(domain, hostno, host, spec_cmd)
        else:
            spec_cmd = f"ssh -p {port} -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -t {background} {user}@{host} "
            spec_cmd += command
            # print("spec_cmd:"+spec_cmd)
            self.run_ssh_passwd(domain, hostno, host, spec_cmd, password)

    def run_command(self, domain_config, spec_host, command):
        '''
        run command
        '''
        self.init_command(domain_config, spec_host, command)

    def run_ssh_passwd(self, domain, hostno, host, cmd, passwd):
        '''
        run ssh by passwd
        '''
        child = pexpect.spawn(cmd)
        try:
            child.expect('(!*)password:(!*)')
            passwd_decode = base64.b64decode(passwd)
            if passwd_decode[-1] == '\n':
                passwd_decode = passwd_decode[:-1]
            _ = child.sendline(passwd_decode)  # base64解码后多一个回车键符，需要剪掉一位
        except pexpect.EOF:
            self.output_info(domain, hostno, host,
                             f"can not connect to {domain}-{hostno}-{host}\n")
            if child.isalive():
                child.close(force=True)
            return
        except pexpect.TIMEOUT:
            self.output_info(domain, hostno, host,
                             f"connect timeout {domain}-{hostno}-{host}\n")
            if child.isalive():
                child.close(force=True)
            return

        child.expect(pexpect.EOF, timeout=60)
        if self.mutex.acquire():
            output_msg = XUtil.decode_msg(child.before)
            self.output_info(domain, hostno, host, output_msg)
        self.mutex.release()
        child.close(force=True)

    def run_ssh_pem(self, domain, hostno, host, cmd):
        '''
        run ssh by pem
        '''
        child = pexpect.spawn(cmd)
        # try:
        #     child.expect('(!*)password:(!*)')
        #     passwd_decode = base64.b64decode(passwd)
        #     if passwd_decode[-1] == '\n':
        #         passwd_decode = passwd_decode[:-1]
        #     _ = child.sendline(passwd_decode)  # base64解码后多一个回车键符，需要剪掉一位
        # except pexpect.EOF:
        #     self.output_info(domain, hostno, host,
        #                      "can not connect to {}-{}-{}\n".format(domain, hostno, host))
        #     if child.isalive():
        #         child.close(force=True)
        #     return
        # except pexpect.TIMEOUT:
        #     self.output_info(domain, hostno, host,
        #                      "connect timeout {}-{}-{}\n".format(domain, hostno, host))
        #     if child.isalive():
        #         child.close(force=True)
        #     return

        child.expect(pexpect.EOF, timeout=60)
        if self.mutex.acquire():
            output_msg = XUtil.decode_msg(child.before)
            self.output_info(domain, hostno, host, output_msg)
        self.mutex.release()
        child.close(force=True)

    def output_info(self, domain, hostno, host, msg):
        '''
        output information
        '''
        index_count = OUT_PUT_WIDTH - \
                    len(STR_OUTPUT_PROMOTE) - \
                    len(domain)- XUtil.str_count(domain) - \
                    len(hostno) - XUtil.str_count(hostno) - \
                    + 3 # space + space + # in format string
        self.map_stdout[host].append("-"*OUT_PUT_WIDTH + "\n")
        self.map_stdout[host].append(
            f"{STR_OUTPUT_PROMOTE}\033[36;1m{domain} {hostno} {host: <{index_count}}\033[0m#\n")
        self.map_stdout[host].append("-"*OUT_PUT_WIDTH + "\n")
        self.map_stdout[host].append(msg)
        #self.map_stdout[host].append("-"*OUT_PUT_WIDTH + "\n")

    def usage(self, command):
        '''
        Usage
        '''
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
    COMMAND = ' '.join(unknowns).replace("\"", "\\\"").replace(
        "$", "\\$")  # .replace("\'", "\\'")
    # print ("{} unknowns:{}".format(args, unknowns))
    time.sleep(0.1)

    if COMMAND == "":
        parser.print_usage()
    else:
        try:
            # command=""
            #print len(sys.argv)
            if COMMAND[-1] == "&":  # 命令行加了&，解析成后台命令
                BACKGROUND = "-f -n"
            else:
                BACKGROUND = ""

            cCRemoteCmd3.run_command(args.domain, args.ip, COMMAND)
            time.sleep(0)
        except KeyboardInterrupt as e:
            print(e)
        except IOError as e:
            print(e)
        except ValueError as e:
            print(e)
        finally:
            pass
