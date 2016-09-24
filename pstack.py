#!/usr/bin/env python
#coding=utf-8

'''
name:
pstack.py
email:
yinglj@asiainfo.com
title:
pstack.py for Linux
'''

import os
import cPickle
import time
import ConfigParser
import re
import string
import logging
import sys
import cmd
import subprocess

class CPStack:

	def __init__(self):
		self.listPstackFiles = [];
		self.listStat = [];
		self.totalThreads = 0;
		self.listIgnores = {"CSocketBase::select":0, "CMDBSyncTableCtrl::get_syncFlag":0, "pthread_cond_wait":0, "nanosleep":0};
		self.mapStatic = {};
		#for v in self.listIgnores:
			#self.listStat.append(0);
		#print self.listIgnores;

	def analyseAllFiles(self):
		for i in range(1, len(sys.argv)):
			self.listPstackFiles.append(sys.argv[i]);
		#print "listPstackFiles", self.listPstackFiles;
		for v in self.listPstackFiles:
			self.analyseOneFile(v);
		self.showResult();

	def analyseOneFile(self, pstack_file):
		if not os.path.exists(pstack_file):
			return True;
		f = file(pstack_file, 'r');
		# if no mode is specified, 'r'ead mode is assumed by default
		stat = 0;
		lines = "";
		self.totalThreads = 0
		while True:
			line = f.readline()
			if len(line) == 0: # Zero length indicates EOF
				break
			if line.find("(Thread ") != -1:
				self.totalThreads += 1
				stat = 1;
				lines = ""
				continue;
			for v in self.listIgnores:
				if line.find(v) != -1:
					stat = 2;
					self.listIgnores[v] += 1
				continue;
			self.staticLine(line);
			lines = lines + line
			if line.find("in clone") != -1 and stat == 1:
				print lines

			#print line, # Notice comma to avoid automatic newline added by Python
		f.close() # close the file
		return True;

	def staticLine(self,line):
			funcName = "";
			split1 = line.split("#");
			if len(split1) > 1:
				split2 = split1[1].split(" from ");
				if len(split2) > 1:
					funcName = "#"+split2[0];
			if self.mapStatic.get(funcName) != None :
				self.mapStatic[funcName] += 1;
			else:
				self.mapStatic[funcName]=1;


	def showResult(self):
        #print self.mapStatic;
        mapStatic = sorted(self.mapStatic.items(), key=lambda d:d[0])   #d[1] 锟斤拷示value
        mapStatic = sorted(mapStatic, key=lambda d:d[0])    #d[1] 锟斤拷示value
        mapStatic = sorted(mapStatic, key=lambda d:d[1])    #d[1] 锟斤拷示value
        for v in mapStatic:
            print "%d\t%s" % (v[1],v[0]),
        print "==========================================================================="
        for v in self.listIgnores:
            print self.listIgnores[v],"\t",v
        print self.totalThreads,"\t","total threads"

def Usage(command):
		print "usage:"+command+" [file]";
		print "example: "+command+" *.pstack.*";
		print "example: "+command+" 12345.pstack.1 12345.pstack.2";

if __name__ == '__main__':
	if len(sys.argv) == 1:
		Usage(sys.argv[0]);
	else:
		try:
			client = CPStack();
			client.analyseAllFiles();
			time.sleep(0);
		except KeyboardInterrupt as e:
			print e
		except IOError as e:
			print e
		except ValueError as e:
			print e
		finally:
			pass;
