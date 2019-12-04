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

import os,sys
import pexpect
import time
import re, collections
import ConfigParser
import threading
import base64
import argparse

mutex = threading.Lock()
cfg = ConfigParser.ConfigParser()
#global spec_host
spec_cmd = ""
cmds = []
background = ""
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

#diff host1 or ip_addr
def init_command(domain_config, spec_host, command):
    read_cfg(sys.path[0]+"/host.cfg")
    #read_cfg(domain_config)
    s = cfg.sections()
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
    domain=""
    thread_list = []
    for i in s:
        #szCmd=""
        user = ""
        password = ""
        host = ""
        workdir = ""
        port = "22"
        for j in cfg.options(i):
            if j == 'user':
                user=cfg.get(i,j)
            if j == 'password':
                password=cfg.get(i,j)
            if j == 'host':
                host=cfg.get(i,j)
            if j == 'port':
                port=cfg.get(i,j)
            if j == 'workdir':
                workdir=cfg.get(i,j)
            if j == 'domain':
                domain=cfg.get(i,j)
        if domain_config != "" and domain_config != "all" and domain != domain_config:
            continue

        if spec_host == i or spec_host == host or spec_host =="":
            my_thread = threading.Thread(target=onethread_run_ssh, args=(user,password,host,port,workdir,command,))
            #print "-------------------1----------------------------------------------------------------------"
            my_thread.start()
            #print "-------------------2----------------------------------------------------------------------"
            thread_list.append(my_thread)
    for thread in thread_list:
        thread.join()

def onethread_run_ssh(user,password,host,port,workdir,command):
    spec_cmd = "ssh -t -p {} -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no {} {}@{} ".format(port, background, user, host)
    spec_cmd += command
    #print "spec_cmd:"+spec_cmd
    run_ssh(host, spec_cmd, password)

def run_command(domain_config, spec_host, command):
    init_command(domain_config, spec_host, command)

def run_ssh(host, cmd, passwd):
    child = pexpect.spawn(cmd)
    try:
        child.expect('(!*)password:(!*)')
        _ = child.sendline(base64.b64decode(passwd)[:-1])    #base64解码后多一个回车键符，需要剪掉一位
    except pexpect.EOF:
        print("pexpect.EOF")
        child.close(force=True)
        return
    except pexpect.TIMEOUT:
        print("pexpect.TIMEOUT")
        child.close(force=True)
        return

    child.expect(pexpect.EOF,timeout=60)
    if mutex.acquire():
        print "-----------------------------------------------------------------------------------------"
        print "# host:"+host
        print "-----------------------------------------------------------------------------------------",
        print child.before,
	mutex.release()
    child.close(force=True)

hostcfg = '''please config filename: host.cfg
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

def Usage(command):
    print "usage:"+command+" [host1] command"
    print hostcfg
    print "example: "+command+" 'ls -l'"
    print "example: "+command+" host1 'ls -l'"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', default='all', help='--domain all')
    parser.add_argument('--ip', default='', help='--ip host_ip')
    args, unknowns = parser.parse_known_args()
    command = ' '.join(unknowns).replace("\"", "\\\"").replace("$", "\\$")#.replace("\'", "\\'")
    #print command
    #print args
    #print "unknowns:{}".format(unknowns)

    if command=="":
        parser.print_usage()
    else:
        try:
            #command=""
            #print len(sys.argv)
            if command[-1]=="&":    #命令行加了&，解析成后台命令
                background = "-f -n"
            else:
                background = ""
    
            run_command(args.domain, args.ip, command)
            time.sleep(0)
        except KeyboardInterrupt as e:
            print e
        except IOError as e:
            print e
        except ValueError as e:
            print e
        finally:
            pass
