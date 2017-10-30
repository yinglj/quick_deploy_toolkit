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

mutex = threading.Lock()
cfg = ConfigParser.ConfigParser();
global spec_host
spec_cmd = ""
cmds = []
def read_cfg(filename):
    cfg.read(filename);
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
def init_command(command):
    read_cfg("./host.cfg");
    s = cfg.sections()
    cmd_argv = [];
    spec_host = ""
    if sys.argv[1] in s:    #host1 in command
        cmd_argv = sys.argv[2:]
        spec_host = sys.argv[1]
    for i in s:
        host = "";
        for j in cfg.options(i):
            if j == 'host':
                host=cfg.get(i,j);
                if host == sys.argv[1]:    #ip in host.cfg
                    spec_host = i
                    cmd_argv = sys.argv[2:]
                break;
    if spec_host == "":
        cmd_argv = sys.argv[1:]    
    for i in cmd_argv:
        command += i+" ";
    #print "command:"+command
    #print "spec_host:"+spec_host
    user = "";
    password = "";
    host = "";
    workdir = "";
    thread_list = []
    for i in s:
        szCmd=""
        user = "";
        password = "";
        host = "";
        workdir = "";
        for j in cfg.options(i):
            if j == 'user':
                user=cfg.get(i,j);
            if j == 'password':
                password=cfg.get(i,j);
            if j == 'host':
                host=cfg.get(i,j);
            if j == 'workdir':
                workdir=cfg.get(i,j);
        if spec_host == i or spec_host =="":
            my_thread = threading.Thread(target=onethread_run_ssh, args=(user,password,host,workdir,command,))
            #print "-------------------1----------------------------------------------------------------------"
            my_thread.start()
            #print "-------------------2----------------------------------------------------------------------"
            thread_list.append(my_thread)
    for thread in thread_list:
        thread.join()

def onethread_run_ssh(user,password,host,workdir,command):
    spec_cmd=szCmd = "ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no "+user+"@"+host+" ";    
    spec_cmd += command
    #print "spec_cmd:"+spec_cmd
    run_ssh(host, spec_cmd, password);

def run_command(command):
    init_command(command)

def run_ssh(host, cmd, passwd):
    child = pexpect.spawn(cmd)
    child.expect('password:')
    log = child.sendline(base64.b64decode(passwd))
    child.expect(pexpect.EOF)
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
user = mongodb
password = oXV4LYH2EUQiHpcg
host = 10.10.13.170
workdir = /home/mongodb
================================================================================
'''

def Usage(command):
    print "usage:"+command+" [host1] command";
    print hostcfg
    print "example: "+command+" 'ls -l'";
    print "example: "+command+" host1 'ls -l'";

if __name__ == '__main__':
    if len(sys.argv) < 2:
        Usage(sys.argv[0]);
    else:
        try:
            command=""
            #print len(sys.argv)
            run_command(command)
            time.sleep(0);
        except KeyboardInterrupt as e:
            print e
        except IOError as e:
            print e
        except ValueError as e:
            print e
        finally:
            pass;
