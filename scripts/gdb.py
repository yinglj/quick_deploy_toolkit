#!/usr/bin/env python
#coding=utf-8

'''
name:
gdb.py
email:
yinglj@asiainfo.com
title:
gdb.py for AIX
'''
from __future__ import print_function
import os
import time
import sys

class CGdb:

    def __init__(self):
        self.listPstackFiles = []
        self.listStat = []
        self.totalThreads = 0
        self.listIgnores = {
            "bvar::PassiveStatus<int>::SeriesSampler::take_sample2":0, 
            "CMDBSyncTableCtrl::get_syncFlag":0, 
            "pthread_cond_wait":0, 
            "nanosleep":0
        }
        self.listContinueCommand = [
            'shell cat /dev/null > ./gdb.output',
            'set logging file ./gdb.output',
            'set logging on',
            'where',
            'set logging off',
            'shell {} {} > {}'.format(os.path.realpath(__file__), './gdb.output', 'gdb.source'),
            'source ./gdb.source',
            #'continue',
        ]
        self.listQuitCommand = {"detach"}
        
        self.mapStatic = {}
        for v in self.listIgnores:
            self.listStat.append(0)
        #print(self.listIgnores)

    def analyseAllFiles(self):
        for i in range(1, len(sys.argv)):
            self.listPstackFiles.append(sys.argv[i])
        #print "listPstackFiles", self.listPstackFiles
        for v in self.listPstackFiles:
            self.analyseOneFile(v)
        #self.showResult()

    def analyseOneFile(self, pstack_file):
        if not os.path.exists(pstack_file):
            return True
        f = file(pstack_file, 'r')
        # if no mode is specified, 'r'ead mode is assumed by default
        stat = 0
        lines = ""
        self.totalThreads = 0
        while True:
            line = f.readline()
            if len(line) == 0: # Zero length indicates EOF
                break
            for v in self.listIgnores:
                if line.find(v) != -1:
                    stat = 2
                    self.listIgnores[v] += 1
                    for i in self.listContinueCommand:
                        print(i)
                    break
        f.close() # close the file
        if stat == 0:
            for i in self.listQuitCommand:
                print(i)
        return True

    def staticLine(self,line):
            funcName = ""
            split1 = line.split("  ")
            if len(split1) > 1:
                split2 = split1[1].split("(0x")
                if len(split2) >= 1:
                    funcName = split2[0]
            if self.mapStatic.get(funcName) != None :
                self.mapStatic[funcName] += 1
            else:
                self.mapStatic[funcName]=1

    def showResult(self):
        mapStatic = sorted(self.mapStatic.items(), key=lambda d:d[0])   #d[1] value
        mapStatic = sorted(mapStatic, key=lambda d:d[0])    #d[1] value
        mapStatic = sorted(mapStatic, key=lambda d:d[1])    #d[1] value
        for v in mapStatic:
            print("{}\t{}".format(v[1],v[0]), end='')
        print("===========================================================================")
        for v in self.listIgnores:
            print('{}{}{}'.format(self.listIgnores[v],"\t",v))
        print('{}{}{}'.format(self.totalThreads,"\t","total threads"))

def Usage(command):
        print("usage:"+command+" [file]")
        print("example: "+command+" *.pstack.*")
        print("example: "+command+" 12345.pstack.1 12345.pstack.2")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        Usage(sys.argv[0])
    else:
        try:
            client = CGdb()
            client.analyseAllFiles()
            time.sleep(0)
        except KeyboardInterrupt as e:
            print(e)
        except IOError as e:
            print(e)
        except ValueError as e:
            print(e)
        finally:
            pass