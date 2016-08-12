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

cfg = ConfigParser.ConfigParser();
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

def run_scp(filename):
	read_cfg('./host.cfg');
	s = cfg.sections()
	user = "";
	password = "";
	host = "";
	workdir = "";
	for i in s:
		szCmd=''
		for j in cfg.options(i):
			if j == 'user':
				user=cfg.get(i,j);
			if j == 'password':
				password=cfg.get(i,j);
			if j == 'host':
				host=cfg.get(i,j);
			if j == 'workdir':
				workdir=cfg.get(i,j);
		szCmd = os.path.dirname(os.path.realpath(__file__))+"/scp.py "+filename+" "+user+" "+password+" "+host+" "+workdir;
		print szCmd;
		pexpect.run(szCmd);	

hostcfg_demo = '''please config filename: host.cfg
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
	print "usage:"+command+" filename";
	print hostcfg_demo
	print "example: "+command+" mongo.tar.gz";

if __name__ == '__main__':
	if len(sys.argv) < 2:
		Usage(sys.argv[0]);
	else:
		try:
			run_scp(sys.argv[1])
			time.sleep(0);
		except KeyboardInterrupt as e:
			print e
		except IOError as e:
			print e
		except ValueError as e:
			print e
		finally:
			pass;
