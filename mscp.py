#!/usr/bin/env python
#coding=utf-8

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

import os, sys
import pexpect
import time
import re, collections
import ConfigParser
import base64
import argparse
import threading

mutex = threading.Lock()
cfg = ConfigParser.ConfigParser()

def read_cfg(filename):
    cfg.read(filename)
    '''
    s = cfg.sections()
    print 'section:', s
    for i in s:
        print cfg.options(i)
        for j in cfg.options(i):
            print j,cfg.get(i, j)
        print cfg.items(i)
    '''


def run_scp(spec_domain, spec_host, filename, spec_dir):
    read_cfg(sys.path[0] + '/host.cfg')
    s = cfg.sections()
    user = ""
    password = ""
    host = ""
    workdir = ""
    port = "22"
    thread_list = []
    for i in s:
        szCmd = ''
        for j in cfg.options(i):
            if j == 'user':
                user = cfg.get(i, j)
            if j == 'password':
                password = cfg.get(i, j)
            if j == 'domain':
                domain = cfg.get(i, j)
            if j == 'host':
                host = cfg.get(i, j)
            if j == 'port':
                port = cfg.get(i, j)
            if j == 'workdir':
                workdir = cfg.get(i, j)
        if spec_dir != "":
            workdir = spec_dir
        if spec_domain != "" and spec_domain != "all" and domain != spec_domain:
            continue
        passwd = base64.b64decode(password)[:-1]    #base64解码后多一个回车键符，需要剪掉一位
        if spec_host == i or spec_host == host or spec_host == "":
            my_thread = threading.Thread(target=onethread_run_scp, args=(port, filename, user, passwd, host, workdir))
            #print "-------------------1----------------------------------------------------------------------"
            my_thread.start()
            #print "-------------------2----------------------------------------------------------------------"
            thread_list.append(my_thread)
    for thread in thread_list:
        thread.join()
    print("="*128)

def onethread_run_scp(port, filename, user, passwd, host, workdir):     
    szCmd = "{}/scp.py {} {} {} {} {} {} ".format(os.path.dirname(os.path.realpath(__file__)), port, filename, user, passwd, host, workdir)
    #print(szCmd)
    #pexpect.run(szCmd)
    (command_output, _) = pexpect.run(szCmd, withexitstatus=1)
    #print("="*128)
    #print command_output
    if mutex.acquire():
        print "="*128
        print "# host:{: <15}{: ^105}#".format(host," ")
        print "{:-^128}".format("-")
        #print command_output.replace("\n\n","\n")
        for line in command_output.split("\n"): #过滤空行
            if line.split():
                print line
	mutex.release()
    

hostcfg_demo = '''please config filename: host.cfg
================================================================================
content example:
[host1]
domain = database
user = mongodb
password = oXV4LYH2EUQiHpcg
host = 10.10.13.170
port = 22
workdir = /home/mongodb
================================================================================
'''

usage_text = "%(prog)s filename\n"
usage_text = usage_text + hostcfg_demo
usage_text = usage_text + "example: %(prog)s mongo.tar.gz\n"
usage_text = usage_text + "example: %(prog)s --domain domain1 mongo.tar.gz\n"
usage_text = usage_text + "example: %(prog)s --host host132 mongo.tar.gz\n"
usage_text = usage_text + "example: %(prog)s --host 10.10.12.132 mongo.tar.gz\n"


def Usage(command):
    print "usage:{} filename".format(command)
    print hostcfg_demo
    print "example: {} mongo.tar.gz".format(command)
    print "example: {} --domain domain1 mongo.tar.gz".format(command)
    print "example: {} --host host132 mongo.tar.gz".format(command)
    print "example: {} --host 10.10.12.132 mongo.tar.gz".format(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0], usage=usage_text)
    parser.add_argument('--domain', default='all', help='--domain all')
    parser.add_argument('--host', default='', help='--host host_ip')
    parser.add_argument('--dir', default='', help='--dir /home/user1/backup/')
    args, unknowns = parser.parse_known_args()
    command = ' '.join(unknowns)

    if len(sys.argv) < 2:
        #Usage(sys.argv[0])
        parser.print_help()
    else:
        try:
            run_scp(args.domain, args.host, command, args.dir)
            #print command
            time.sleep(0)
        except KeyboardInterrupt as e:
            print e
        except IOError as e:
            print e
        except ValueError as e:
            print e
        finally:
            pass