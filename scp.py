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

def run_scp():
	szCmd = "scp -o StrictHostKeyChecking=no "+sys.argv[1]+" "+sys.argv[2]+"@"+sys.argv[4]+":"+sys.argv[5]
    print szCmd;
	child = pexpect.spawn(szCmd)
	child.expect('(!*)password:(!*)')
	log = child.sendline(sys.argv[3])
	child.expect(pexpect.EOF)	#wait for end of the command
	print child.before
	child.close(force=True)

def Usage(command):
	print "usage:"+command+" file user userpasswd ip_addr dir";
	print "example: "+command+" abc.tar.gz root password123 10.10.13.181 /home/mongo/";

if __name__ == '__main__':
	if len(sys.argv) <= 5:
		Usage(sys.argv[0]);
	else:
		try:
			run_scp()
			time.sleep(0);
		except KeyboardInterrupt as e:
			print e
		except IOError as e:
			print e
		except ValueError as e:
			print e
		finally:
			pass;
